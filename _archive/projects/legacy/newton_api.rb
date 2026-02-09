#!/usr/bin/env ruby
# ═══════════════════════════════════════════════════════════════════════════
# NEWTON API v1.0.0
# The State Machine for AI
#
# Every transition is verified. Every state change is logged.
# 1 == 1
#
# Author: Jared Lewis | Ada Computing Company | Houston, Texas
# ═══════════════════════════════════════════════════════════════════════════

require 'sinatra'
require 'sinatra/json'
require 'json'
require 'openssl'
require 'digest'
require 'base64'
require 'securerandom'
require 'time'
require 'fileutils'

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

set :port, ENV['PORT'] || 4567
set :bind, '0.0.0.0'
set :protection, except: [:json_csrf]

configure do
  enable :cross_origin rescue nil
end

before do
  content_type :json
  headers 'Access-Control-Allow-Origin' => '*',
          'Access-Control-Allow-Methods' => 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers' => 'Content-Type'
end

options '*' do
  200
end

# ═══════════════════════════════════════════════════════════════════════════
# NEWTON CORE
# ═══════════════════════════════════════════════════════════════════════════

module Newton
  VERSION = '1.0.0'

  # States
  STATES = {
    pending: 'PENDING',
    verified: 'VERIFIED',
    rejected: 'REJECTED',
    executing: 'EXECUTING',
    committed: 'COMMITTED',
    rolled_back: 'ROLLED_BACK'
  }.freeze

  # ─────────────────────────────────────────────────────────────────────────
  # FORGE - State transition logic
  # ─────────────────────────────────────────────────────────────────────────
  class Forge
    def self.process(intent, ledger)
      return nil if intent.to_s.strip.length < 4

      intent = intent.to_s.strip
      count = ledger.count { |e| e[:name] == intent } + 1
      z = [10.0 - (count * 3.33), 0.0].max.round(2)

      {
        id: "N_#{SecureRandom.hex(4).upcase}",
        name: intent,
        z: z,
        status: z <= 0 ? STATES[:verified] : STATES[:pending],
        timestamp: Time.now.to_i,
        fingerprint: generate_fingerprint(intent)
      }
    end

    def self.generate_fingerprint(input)
      Digest::SHA256.hexdigest("#{input}#{Time.now.to_i}#{SecureRandom.hex(4)}")[0, 12].upcase
    end
  end

  # ─────────────────────────────────────────────────────────────────────────
  # VAULT - Encrypted storage
  # ─────────────────────────────────────────────────────────────────────────
  class Vault
    def initialize(owner)
      @owner = owner
      @path = File.join(storage_dir, "#{safe_filename(owner)}.vault")
    end

    def save(ledger)
      key = derive_key(@owner)
      cipher = OpenSSL::Cipher.new('AES-256-CBC').encrypt
      cipher.key = key
      iv = cipher.random_iv
      encrypted = cipher.update(ledger.to_json) + cipher.final

      data = {
        iv: Base64.strict_encode64(iv),
        data: Base64.strict_encode64(encrypted),
        version: VERSION,
        updated: Time.now.iso8601
      }

      File.write(@path, data.to_json)
      true
    rescue => e
      puts "Vault save error: #{e.message}"
      false
    end

    def load
      return [] unless File.exist?(@path)

      raw = JSON.parse(File.read(@path))
      key = derive_key(@owner)
      cipher = OpenSSL::Cipher.new('AES-256-CBC').decrypt
      cipher.key = key
      cipher.iv = Base64.strict_decode64(raw['iv'])

      JSON.parse(
        cipher.update(Base64.strict_decode64(raw['data'])) + cipher.final,
        symbolize_names: true
      )
    rescue => e
      puts "Vault load error: #{e.message}"
      []
    end

    private

    def derive_key(owner)
      Digest::SHA256.digest("Newton_#{owner}_v#{VERSION}")
    end

    def safe_filename(name)
      name.gsub(/[^a-zA-Z0-9_-]/, '_')[0, 64]
    end

    def storage_dir
      dir = ENV['NEWTON_STORAGE'] || File.join(Dir.home, '.newton')
      FileUtils.mkdir_p(dir) unless Dir.exist?(dir)
      dir
    end
  end

  # ─────────────────────────────────────────────────────────────────────────
  # BRIDGE - Export and packaging
  # ─────────────────────────────────────────────────────────────────────────
  class Bridge
    def self.package(ledger, owner)
      verified = ledger.select { |e| e[:status] == STATES[:verified] }
                       .uniq { |e| e[:name] }

      payload = {
        owner: owner,
        created: Time.now.iso8601,
        version: VERSION,
        count: verified.length,
        items: verified.map { |t|
          {
            name: t[:name],
            fingerprint: t[:fingerprint],
            timestamp: t[:timestamp]
          }
        }
      }

      encoded = Base64.strict_encode64(payload.to_json)
      signature = Digest::SHA256.hexdigest(encoded)[0, 16].upcase

      {
        payload: payload,
        encoded: encoded,
        signature: signature
      }
    end

    def self.verify_package(encoded, signature)
      computed = Digest::SHA256.hexdigest(encoded)[0, 16].upcase
      computed == signature
    end
  end

  # ─────────────────────────────────────────────────────────────────────────
  # ENGINE - Main API logic
  # ─────────────────────────────────────────────────────────────────────────
  class Engine
    attr_reader :owner, :ledger

    def initialize(owner)
      @owner = owner
      @vault = Vault.new(owner)
      @ledger = @vault.load
    end

    def make(intent)
      result = Forge.process(intent, @ledger)
      return { error: 'Intent too short (min 4 chars)', code: 400 } unless result

      @ledger << result
      @vault.save(@ledger)

      {
        id: result[:id],
        intent: result[:name],
        z: result[:z],
        status: result[:status],
        fingerprint: result[:fingerprint],
        timestamp: result[:timestamp],
        remaining: result[:status] == STATES[:pending] ? (result[:z] / 3.33).ceil : 0
      }
    end

    def verify(fingerprint)
      entry = @ledger.find { |e| e[:fingerprint] == fingerprint }

      return { exists: false, fingerprint: fingerprint } unless entry

      {
        exists: true,
        fingerprint: fingerprint,
        intent: entry[:name],
        status: entry[:status],
        z: entry[:z],
        timestamp: entry[:timestamp]
      }
    end

    def audit
      grouped = @ledger.group_by { |e| e[:name] }

      entries = grouped.map do |name, items|
        latest = items.last
        {
          intent: name,
          status: latest[:status],
          z: latest[:z],
          commits: items.length,
          fingerprint: latest[:fingerprint],
          first_seen: items.first[:timestamp],
          last_seen: latest[:timestamp]
        }
      end

      verified_count = entries.count { |e| e[:status] == STATES[:verified] }
      pending_count = entries.count { |e| e[:status] == STATES[:pending] }

      {
        owner: @owner,
        total_entries: @ledger.length,
        unique_intents: entries.length,
        verified: verified_count,
        pending: pending_count,
        entries: entries
      }
    end

    def package
      Bridge.package(@ledger, @owner)
    end

    def execute(fingerprint, action)
      entry = @ledger.find { |e| e[:fingerprint] == fingerprint }

      return { error: 'Fingerprint not found', code: 404 } unless entry
      return { error: 'Intent not verified', code: 403 } unless entry[:status] == STATES[:verified]

      # Record execution attempt
      execution = {
        id: "X_#{SecureRandom.hex(4).upcase}",
        fingerprint: fingerprint,
        action: action,
        status: STATES[:executing],
        started: Time.now.to_i
      }

      begin
        # Here's where adapters would plug in
        # For now, we just record the execution
        result = yield(entry, action) if block_given?

        execution[:status] = STATES[:committed]
        execution[:completed] = Time.now.to_i
        execution[:result] = result

        @ledger << {
          id: execution[:id],
          name: "EXEC:#{entry[:name]}",
          status: STATES[:committed],
          fingerprint: Forge.generate_fingerprint("#{fingerprint}:#{action}"),
          timestamp: execution[:completed],
          parent: fingerprint
        }
        @vault.save(@ledger)

        execution
      rescue => e
        execution[:status] = STATES[:rolled_back]
        execution[:error] = e.message
        execution[:completed] = Time.now.to_i

        @ledger << {
          id: execution[:id],
          name: "ROLLBACK:#{entry[:name]}",
          status: STATES[:rolled_back],
          fingerprint: Forge.generate_fingerprint("#{fingerprint}:rollback"),
          timestamp: execution[:completed],
          parent: fingerprint,
          error: e.message
        }
        @vault.save(@ledger)

        execution
      end
    end
  end
end

# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════════

# Health check
get '/' do
  json({
    service: 'Newton API',
    version: Newton::VERSION,
    status: 'operational',
    invariant: '1 == 1',
    timestamp: Time.now.iso8601
  })
end

get '/health' do
  json({ status: 'ok', version: Newton::VERSION })
end

# ─────────────────────────────────────────────────────────────────────────
# POST /make
# Commit an intent to the ledger
# ─────────────────────────────────────────────────────────────────────────
post '/make' do
  data = JSON.parse(request.body.read) rescue {}

  owner = data['owner']&.strip
  intent = data['intent']&.strip

  return json({ error: 'Missing owner', code: 400 }) unless owner && !owner.empty?
  return json({ error: 'Missing intent', code: 400 }) unless intent && !intent.empty?

  engine = Newton::Engine.new(owner)
  result = engine.make(intent)

  status result[:code] || 200
  json(result)
end

# ─────────────────────────────────────────────────────────────────────────
# GET /verify/:fingerprint
# Check if a fingerprint exists and its status
# ─────────────────────────────────────────────────────────────────────────
get '/verify/:fingerprint' do
  fingerprint = params[:fingerprint]&.upcase
  owner = params[:owner]&.strip

  return json({ error: 'Missing owner', code: 400 }) unless owner && !owner.empty?

  engine = Newton::Engine.new(owner)
  result = engine.verify(fingerprint)

  json(result)
end

# ─────────────────────────────────────────────────────────────────────────
# GET /audit/:owner
# Retrieve the full audit log for an owner
# ─────────────────────────────────────────────────────────────────────────
get '/audit/:owner' do
  owner = params[:owner]&.strip

  return json({ error: 'Missing owner', code: 400 }) unless owner && !owner.empty?

  engine = Newton::Engine.new(owner)
  result = engine.audit

  json(result)
end

# ─────────────────────────────────────────────────────────────────────────
# POST /package
# Export verified intents as a signed package
# ─────────────────────────────────────────────────────────────────────────
post '/package' do
  data = JSON.parse(request.body.read) rescue {}

  owner = data['owner']&.strip

  return json({ error: 'Missing owner', code: 400 }) unless owner && !owner.empty?

  engine = Newton::Engine.new(owner)
  result = engine.package

  json(result)
end

# ─────────────────────────────────────────────────────────────────────────
# POST /verify-package
# Verify a signed package
# ─────────────────────────────────────────────────────────────────────────
post '/verify-package' do
  data = JSON.parse(request.body.read) rescue {}

  encoded = data['encoded']
  signature = data['signature']&.upcase

  return json({ error: 'Missing encoded payload', code: 400 }) unless encoded
  return json({ error: 'Missing signature', code: 400 }) unless signature

  valid = Newton::Bridge.verify_package(encoded, signature)

  if valid
    payload = JSON.parse(Base64.strict_decode64(encoded))
    json({ valid: true, payload: payload })
  else
    json({ valid: false, error: 'Signature mismatch' })
  end
end

# ─────────────────────────────────────────────────────────────────────────
# POST /execute
# Execute an action against a verified intent
# ─────────────────────────────────────────────────────────────────────────
post '/execute' do
  data = JSON.parse(request.body.read) rescue {}

  owner = data['owner']&.strip
  fingerprint = data['fingerprint']&.upcase
  action = data['action']

  return json({ error: 'Missing owner', code: 400 }) unless owner && !owner.empty?
  return json({ error: 'Missing fingerprint', code: 400 }) unless fingerprint
  return json({ error: 'Missing action', code: 400 }) unless action

  engine = Newton::Engine.new(owner)

  result = engine.execute(fingerprint, action) do |entry, act|
    # This is where adapters would plug in
    # For now, just echo the action
    { executed: true, intent: entry[:name], action: act }
  end

  status result[:code] || 200
  json(result)
end

# ─────────────────────────────────────────────────────────────────────────
# POST /transition
# Generic state transition (for adapter integration)
# ─────────────────────────────────────────────────────────────────────────
post '/transition' do
  data = JSON.parse(request.body.read) rescue {}

  owner = data['owner']&.strip
  intent = data['intent']&.strip
  adapter = data['adapter'] || 'default'
  action = data['action']

  return json({ error: 'Missing owner', code: 400 }) unless owner && !owner.empty?
  return json({ error: 'Missing intent', code: 400 }) unless intent && !intent.empty?

  engine = Newton::Engine.new(owner)

  # Step 1: Commit intent
  make_result = engine.make(intent)

  # Step 2: If not verified, return pending state
  unless make_result[:status] == Newton::STATES[:verified]
    return json({
      phase: 'pending',
      intent: make_result,
      message: "Intent requires #{make_result[:remaining]} more commits to verify"
    })
  end

  # Step 3: Execute if action provided and intent is verified
  if action
    exec_result = engine.execute(make_result[:fingerprint], action) do |entry, act|
      # Adapter integration point
      { adapter: adapter, intent: entry[:name], action: act, timestamp: Time.now.to_i }
    end

    return json({
      phase: 'executed',
      intent: make_result,
      execution: exec_result
    })
  end

  json({
    phase: 'verified',
    intent: make_result,
    message: 'Intent verified. Provide action to execute.'
  })
end

# ═══════════════════════════════════════════════════════════════════════════
# ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════

not_found do
  json({ error: 'Not found', code: 404 })
end

error do
  json({ error: 'Internal error', code: 500, message: env['sinatra.error'].message })
end

# ═══════════════════════════════════════════════════════════════════════════
# START
# ═══════════════════════════════════════════════════════════════════════════

if __FILE__ == $0
  puts <<~BANNER

    ═══════════════════════════════════════════════════════════════
                           NEWTON API
                    The State Machine for AI
    ═══════════════════════════════════════════════════════════════

    Version: #{Newton::VERSION}
    Invariant: 1 == 1

    Endpoints:
      POST /make          - Commit an intent
      GET  /verify/:fp    - Verify a fingerprint
      GET  /audit/:owner  - Full audit log
      POST /package       - Export signed package
      POST /execute       - Execute verified action
      POST /transition    - Full state transition

    © 2025 Jared Lewis · Ada Computing Company · Jared Lewis Conglomerate - Houston

    ═══════════════════════════════════════════════════════════════

  BANNER

  set :port, ENV['PORT'] || 4567
  set :bind, '0.0.0.0'
end
