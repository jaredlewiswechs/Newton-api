#!/usr/bin/env ruby
# ═══════════════════════════════════════════════════════════════════════════
# NEWTON UNIVERSAL ADAPTER v1.0.0
# The Vendor Agnostic Bridge
#
# Usage:
#   VENDOR=claude NEWTON_KEY=sk-ant-xxx ruby adapter_universal.rb
#   VENDOR=groq NEWTON_KEY=gsk_xxx ruby adapter_universal.rb
#   VENDOR=local ruby adapter_universal.rb
#
# Author: Jared Lewis | Ada Computing Company | Houston, Texas
# ═══════════════════════════════════════════════════════════════════════════

require 'net/http'
require 'json'
require 'uri'

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

NEWTON_HOST = ENV['NEWTON_HOST'] || "https://your-app-name.onrender.com"
SELECTED_VENDOR = ENV['VENDOR'] || 'claude'
VERSION = '1.0.0'

# ═══════════════════════════════════════════════════════════════════════════
# VENDOR IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════

class BaseVendor
  def name
    raise NotImplementedError
  end

  def generate(intent)
    raise NotImplementedError
  end

  protected

  def extract_json(text)
    return nil unless text
    match = text.match(/\{.*\}/m)
    match ? JSON.parse(match[0]) : nil
  rescue JSON::ParserError
    nil
  end

  def http_post(uri, headers, body)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = uri.scheme == 'https'
    http.open_timeout = 10
    http.read_timeout = 60

    req = Net::HTTP::Post.new(uri.path)
    headers.each { |k, v| req[k] = v }
    req.body = body.to_json

    http.request(req)
  end
end

class ClaudeVendor < BaseVendor
  API_URL = "https://api.anthropic.com/v1/messages"

  def initialize(key)
    @key = key
  end

  def name
    "Anthropic Claude"
  end

  def generate(intent)
    uri = URI(API_URL)
    headers = {
      'x-api-key' => @key,
      'anthropic-version' => '2023-06-01',
      'Content-Type' => 'application/json'
    }
    body = {
      model: "claude-sonnet-4-20250514",
      max_tokens: 512,
      system: "You are an execution engine. Output ONLY a valid JSON object representing the action to take. No markdown, no explanation, no code blocks. Just the raw JSON object.",
      messages: [{ role: "user", content: "Generate action JSON for: #{intent}" }]
    }

    res = http_post(uri, headers, body)

    if res.code == '200'
      data = JSON.parse(res.body)
      content = data.dig('content', 0, 'text')
      extract_json(content)
    else
      puts "   [!] Claude API Error: #{res.code} - #{res.body[0..200]}"
      nil
    end
  rescue => e
    puts "   [!] Claude Error: #{e.message}"
    nil
  end
end

class GroqVendor < BaseVendor
  API_URL = "https://api.groq.com/openai/v1/chat/completions"

  def initialize(key)
    @key = key
  end

  def name
    "Groq (Llama 3)"
  end

  def generate(intent)
    uri = URI(API_URL)
    headers = {
      'Authorization' => "Bearer #{@key}",
      'Content-Type' => 'application/json'
    }
    body = {
      model: "llama3-70b-8192",
      messages: [
        { role: "system", content: "Output ONLY a valid JSON object. No explanation." },
        { role: "user", content: "Generate action JSON for: #{intent}" }
      ],
      response_format: { type: "json_object" },
      temperature: 0.1
    }

    res = http_post(uri, headers, body)

    if res.code == '200'
      data = JSON.parse(res.body)
      content = data.dig('choices', 0, 'message', 'content')
      JSON.parse(content)
    else
      puts "   [!] Groq API Error: #{res.code}"
      nil
    end
  rescue => e
    puts "   [!] Groq Error: #{e.message}"
    nil
  end
end

class OpenAIVendor < BaseVendor
  API_URL = "https://api.openai.com/v1/chat/completions"

  def initialize(key)
    @key = key
  end

  def name
    "OpenAI GPT-4"
  end

  def generate(intent)
    uri = URI(API_URL)
    headers = {
      'Authorization' => "Bearer #{@key}",
      'Content-Type' => 'application/json'
    }
    body = {
      model: "gpt-4o",
      messages: [
        { role: "system", content: "Output ONLY a valid JSON object. No explanation." },
        { role: "user", content: "Generate action JSON for: #{intent}" }
      ],
      response_format: { type: "json_object" },
      temperature: 0.1
    }

    res = http_post(uri, headers, body)

    if res.code == '200'
      data = JSON.parse(res.body)
      content = data.dig('choices', 0, 'message', 'content')
      JSON.parse(content)
    else
      puts "   [!] OpenAI API Error: #{res.code}"
      nil
    end
  rescue => e
    puts "   [!] OpenAI Error: #{e.message}"
    nil
  end
end

class LocalVendor < BaseVendor
  API_URL = "http://localhost:11434/api/generate"

  def initialize(_key = nil)
  end

  def name
    "Ollama (Local)"
  end

  def generate(intent)
    uri = URI(API_URL)

    http = Net::HTTP.new(uri.host, uri.port)
    http.open_timeout = 5
    http.read_timeout = 120

    req = Net::HTTP::Post.new(uri.path)
    req['Content-Type'] = 'application/json'
    req.body = {
      model: ENV['OLLAMA_MODEL'] || "mistral",
      prompt: "Output ONLY a JSON object for this action: #{intent}",
      format: "json",
      stream: false
    }.to_json

    res = http.request(req)

    if res.code == '200'
      data = JSON.parse(res.body)
      JSON.parse(data['response'])
    else
      puts "   [!] Ollama Error: #{res.code}"
      nil
    end
  rescue Errno::ECONNREFUSED
    puts "   [!] Ollama not running. Start with: ollama serve"
    nil
  rescue => e
    puts "   [!] Local Error: #{e.message}"
    nil
  end
end

# ═══════════════════════════════════════════════════════════════════════════
# VENDOR FACTORY
# ═══════════════════════════════════════════════════════════════════════════

class VendorFactory
  VENDORS = {
    'claude' => ClaudeVendor,
    'anthropic' => ClaudeVendor,
    'groq' => GroqVendor,
    'llama' => GroqVendor,
    'openai' => OpenAIVendor,
    'gpt' => OpenAIVendor,
    'local' => LocalVendor,
    'ollama' => LocalVendor
  }.freeze

  def self.create(type, key)
    vendor_class = VENDORS[type.to_s.downcase] || ClaudeVendor
    vendor_class.new(key)
  end

  def self.available
    VENDORS.keys.uniq
  end
end

# ═══════════════════════════════════════════════════════════════════════════
# UNIVERSAL ADAPTER
# ═══════════════════════════════════════════════════════════════════════════

class UniversalAdapter
  attr_reader :vendor

  def initialize(owner, api_key)
    @owner = owner
    @api_key = api_key
    @vendor = VendorFactory.create(SELECTED_VENDOR, api_key)
    check_connection
  end

  def check_connection
    puts "[-] Pinging Newton Kernel at #{NEWTON_HOST}..."
    uri = URI("#{NEWTON_HOST}/health")

    begin
      http = Net::HTTP.new(uri.host, uri.port)
      http.use_ssl = uri.scheme == 'https'
      http.open_timeout = 10
      http.read_timeout = 10

      res = http.get(uri.path)

      if res.is_a?(Net::HTTPSuccess)
        data = JSON.parse(res.body)
        puts "[✓] Kernel Active. Version: #{data['version'] || '1.0'}"
        puts "[✓] Vendor: #{@vendor.name}"
        puts "[✓] Owner: #{@owner}"
        puts ""
      else
        abort "[!] Kernel Error: HTTP #{res.code}"
      end
    rescue Errno::ECONNREFUSED
      abort "[!] Connection Refused. Is the kernel running at #{NEWTON_HOST}?"
    rescue => e
      abort "[!] Connection Failed: #{e.message}"
    end
  end

  def resolve(intent)
    puts "\n══════════════════════════════════════════════════════════════"
    puts "   SOVEREIGN TRANSACTION"
    puts "══════════════════════════════════════════════════════════════"
    puts "   Intent:  \"#{intent}\""
    puts "   Vendor:  #{@vendor.name}"
    puts "   Owner:   #{@owner}"
    puts "──────────────────────────────────────────────────────────────"

    # 1. COMMIT TO LEDGER
    state = post_to_kernel("/make", { owner: @owner, intent: intent })

    if state['error']
      puts "   [!] Error: #{state['error']}"
      return
    end

    # 2. VERIFICATION LOOP (The Z-Score Grind)
    loop_count = 0
    while state['status'] == 'PENDING'
      loop_count += 1
      puts ""
      puts "   [#{state['status']}] Z-Score: #{state['z']}"
      puts "   Fingerprint: #{state['fingerprint']}"
      puts "   Remaining commits: #{state['remaining']}"
      puts ""
      print "   >  Verify this intent? (y/n): "

      confirm = gets&.chomp&.downcase

      unless confirm == 'y'
        puts ""
        puts "   [×] Transaction aborted by user."
        return
      end

      state = post_to_kernel("/make", { owner: @owner, intent: intent })

      if state['error']
        puts "   [!] Error: #{state['error']}"
        return
      end
    end

    # 3. CRYSTALLIZED - Intent Verified
    puts ""
    puts "──────────────────────────────────────────────────────────────"
    puts "   [✓] VERIFIED"
    puts "   Z-Score: #{state['z']}"
    puts "   Fingerprint: #{state['fingerprint']}"
    puts "   1 == 1"
    puts "──────────────────────────────────────────────────────────────"

    # 4. VENDOR EXECUTION (Now we call the LLM)
    puts ""
    puts "   [-] Engaging #{@vendor.name}..."

    action = @vendor.generate(state['intent'])

    unless action
      puts "   [!] Vendor failed to generate valid action."
      return
    end

    puts "   [✓] Action generated:"
    puts "       #{action.to_json}"

    # 5. COMMIT EXECUTION TO LEDGER
    puts ""
    puts "   [-] Committing execution to ledger..."

    result = post_to_kernel("/execute", {
      owner: @owner,
      fingerprint: state['fingerprint'],
      action: action
    })

    if result['error']
      puts "   [!] Execution Error: #{result['error']}"
      return
    end

    puts ""
    puts "══════════════════════════════════════════════════════════════"
    puts "   [✓] COMMITTED"
    puts "══════════════════════════════════════════════════════════════"
    puts "   Execution ID: #{result['id']}"
    puts "   Status: #{result['status']}"
    puts "   Fingerprint: #{state['fingerprint']}"
    puts "══════════════════════════════════════════════════════════════"
  end

  def audit
    result = get_from_kernel("/audit/#{URI.encode_www_form_component(@owner)}")

    puts "\n══════════════════════════════════════════════════════════════"
    puts "   AUDIT LEDGER: #{@owner}"
    puts "══════════════════════════════════════════════════════════════"
    puts "   Total Entries: #{result['total_entries']}"
    puts "   Unique Intents: #{result['unique_intents']}"
    puts "   Verified: #{result['verified']}"
    puts "   Pending: #{result['pending']}"
    puts "──────────────────────────────────────────────────────────────"

    result['entries']&.each do |entry|
      status_icon = entry['status'] == 'VERIFIED' ? '✓' : '○'
      puts "   [#{status_icon}] #{entry['intent']}"
      puts "       Z: #{entry['z']} | Commits: #{entry['commits']} | FP: #{entry['fingerprint']}"
    end

    puts "══════════════════════════════════════════════════════════════"
  end

  private

  def post_to_kernel(endpoint, payload)
    uri = URI("#{NEWTON_HOST}#{endpoint}")
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = uri.scheme == 'https'
    http.open_timeout = 10
    http.read_timeout = 30

    req = Net::HTTP::Post.new(uri.path)
    req['Content-Type'] = 'application/json'
    req.body = payload.to_json

    res = http.request(req)
    JSON.parse(res.body)
  rescue => e
    { 'error' => e.message }
  end

  def get_from_kernel(endpoint)
    uri = URI("#{NEWTON_HOST}#{endpoint}")
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = uri.scheme == 'https'
    http.open_timeout = 10
    http.read_timeout = 30

    res = http.get(uri.path)
    JSON.parse(res.body)
  rescue => e
    { 'error' => e.message }
  end
end

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __FILE__ == $0
  puts <<~BANNER

    ═══════════════════════════════════════════════════════════════
                    NEWTON UNIVERSAL ADAPTER v#{VERSION}
                       The Vendor Agnostic Bridge
    ═══════════════════════════════════════════════════════════════

    Available vendors: #{VendorFactory.available.join(', ')}
    Selected vendor:   #{SELECTED_VENDOR}
    Newton kernel:     #{NEWTON_HOST}

    Commands:
      [intent]   Process an intent through Newton
      audit      Show your ledger
      exit       Quit

    ═══════════════════════════════════════════════════════════════

  BANNER

  # Get configuration
  owner = ENV['NEWTON_OWNER']
  key = ENV['NEWTON_KEY'] || ARGV[0]

  unless owner
    print "Owner ID: "
    owner = gets&.chomp
  end

  if SELECTED_VENDOR != 'local' && !key
    print "API Key (#{SELECTED_VENDOR}): "
    key = gets&.chomp
  end

  abort "Owner required." if owner.nil? || owner.empty?
  abort "API key required for #{SELECTED_VENDOR}." if SELECTED_VENDOR != 'local' && (key.nil? || key.empty?)

  # Initialize adapter
  adapter = UniversalAdapter.new(owner, key)

  # Main loop
  loop do
    print "\nNewton (#{adapter.vendor.name})> "
    input = gets&.chomp

    break if input.nil? || input.downcase == 'exit'
    next if input.empty?

    case input.downcase
    when 'audit'
      adapter.audit
    when 'help'
      puts "\nCommands: [intent], audit, exit"
    else
      adapter.resolve(input)
    end
  end

  puts "\n1 == 1. The math is solid.\n\n"
end
