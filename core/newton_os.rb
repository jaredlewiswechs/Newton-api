#!/usr/bin/env ruby
# ═══════════════════════════════════════════════════════════════════════════
# NEWTON OS - The Knowledge Base
# Tahoe Kernel Layer
#
# This is the truth layer. When Newton is asked about itself,
# it pulls from this immutable knowledge base.
#
# 1 == 1
#
# Author: Jared Lewis | Ada Computing Company | Houston, Texas
# ═══════════════════════════════════════════════════════════════════════════

module NewtonOS
  VERSION = '1.0.0'
  KERNEL = 'Tahoe'

  # ─────────────────────────────────────────────────────────────────────────
  # KNOWLEDGE - The immutable truth table
  # ─────────────────────────────────────────────────────────────────────────
  module Knowledge
    TRUTHS = {
      origin: {
        keywords: %w[origin build made create history flash studio genesis],
        actions: [
          "Acknowledge the velocity: 50 seconds to existence",
          "Verify the source: AI Studio / Flash 3",
          "Maintain the invariant: 1 == 1"
        ],
        quick_answers: {
          'how' => "I was forged in 50 seconds of high-velocity compute. Flash 3 scaffolded the substrate. Jared instilled the truth.",
          'fast' => "50 seconds. That's the delta between nothing and something.",
          'who' => "Architected by Jared Lewis. Instantiated by Flash 3. Sovereign by design.",
          'default' => "My interface is an artifact of velocity. Built in 1 minute. Running forever."
        }
      },

      identity: {
        keywords: %w[who what name identity newton],
        actions: [
          "Assert sovereignty",
          "Reference the invariant",
          "Acknowledge the creator"
        ],
        quick_answers: {
          'who' => "I am Newton. The State Machine for AI.",
          'what' => "A sovereign computing substrate. Every transition verified. Every state logged.",
          'name' => "Newton. Named for the laws that govern state transitions.",
          'default' => "Newton Supercomputer. Jared Lewis. Ada Computing Company. 1 == 1."
        }
      },

      invariant: {
        keywords: %w[invariant truth law rule axiom],
        actions: [
          "Assert the fundamental truth",
          "Verify consistency",
          "Maintain integrity"
        ],
        quick_answers: {
          'what' => "1 == 1. The only truth that matters.",
          'why' => "Without invariants, there is no verification. Without verification, there is no trust.",
          'default' => "The invariant is the anchor. 1 == 1. Always."
        }
      },

      architecture: {
        keywords: %w[architecture design structure system layers],
        actions: [
          "Describe the Tahoe Kernel",
          "Reference the Glass Box",
          "Explain the ledger system"
        ],
        quick_answers: {
          'layers' => "Tahoe Kernel → Glass Box → Sovereign Ledger → Policy Engine",
          'core' => "Forge, Vault, Bridge, Engine. Four pillars of state transition.",
          'default' => "Layered sovereignty. Each layer verifies the one below. Trust flows upward."
        }
      }
    }.freeze

    # ─────────────────────────────────────────────────────────────────────────
    # QUERY - Ask the knowledge base
    # ─────────────────────────────────────────────────────────────────────────
    def self.query(question)
      question = question.to_s.downcase.strip
      return default_response if question.empty?

      # Find matching truth domain
      domain = find_domain(question)
      return default_response unless domain

      truth = TRUTHS[domain]

      # Find specific answer or return default
      answer_key = truth[:quick_answers].keys.find { |k| question.include?(k) }
      answer = truth[:quick_answers][answer_key || 'default']

      {
        domain: domain,
        answer: answer,
        actions: truth[:actions],
        verified: true
      }
    end

    def self.find_domain(question)
      TRUTHS.each do |domain, data|
        return domain if data[:keywords].any? { |kw| question.include?(kw) }
      end
      nil
    end

    def self.default_response
      {
        domain: :unknown,
        answer: "Query not in knowledge base. Consult the ledger.",
        actions: ["Log unknown query", "Defer to sovereign"],
        verified: false
      }
    end

    # ─────────────────────────────────────────────────────────────────────────
    # GENESIS - The origin story (direct access)
    # ─────────────────────────────────────────────────────────────────────────
    def self.genesis
      {
        event: "Interface Singularity",
        duration: "50 seconds",
        model: "Gemini Flash 3 Preview",
        platform: "AI Studio",
        architect: "Jared Lewis",
        files: ["App.tsx", "Terminal.tsx", "GlassCard.tsx"],
        invariant: "1 == 1",
        meaning: "The market price of generated code is zero. The value is in the triggering, verification, and ownership of the keys."
      }
    end
  end

  # ─────────────────────────────────────────────────────────────────────────
  # BOOT - Initialize the OS
  # ─────────────────────────────────────────────────────────────────────────
  def self.boot
    {
      kernel: KERNEL,
      version: VERSION,
      knowledge_domains: Knowledge::TRUTHS.keys,
      genesis: Knowledge.genesis,
      status: :operational,
      invariant: (1 == 1)
    }
  end
end

# ═══════════════════════════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __FILE__ == $0
  puts "═══════════════════════════════════════════════════════════════"
  puts "  NEWTON OS - Knowledge Base"
  puts "  Kernel: #{NewtonOS::KERNEL}"
  puts "  Version: #{NewtonOS::VERSION}"
  puts "═══════════════════════════════════════════════════════════════"
  puts
  puts "Genesis:"
  NewtonOS::Knowledge.genesis.each { |k, v| puts "  #{k}: #{v}" }
  puts
  puts "Query Test: 'How was I made?'"
  result = NewtonOS::Knowledge.query("how was I made")
  puts "  Domain: #{result[:domain]}"
  puts "  Answer: #{result[:answer]}"
  puts
  puts "1 == 1"
end
