#!/usr/bin/env ruby
# ═══════════════════════════════════════════════════════════════════════════
# NEWTON TAHOE - The Display Kernel
# PixelEngine for Terminal Rendering
#
# Every pixel is intentional. Every frame is verified.
# Flash-3 Instantiated // 50s
#
# 1 == 1
#
# Author: Jared Lewis | Ada Computing Company | Houston, Texas
# ═══════════════════════════════════════════════════════════════════════════

require_relative 'newton_os'

module NewtonTahoe
  VERSION = '1.0.0'

  # Display constants
  WIDTH = 80
  BAR = '─'
  DOUBLE_BAR = '═'

  # ─────────────────────────────────────────────────────────────────────────
  # PIXEL ENGINE - Terminal rendering
  # ─────────────────────────────────────────────────────────────────────────
  module PixelEngine
    MODES = {
      normal: { color: "\e[0m", prefix: "" },
      success: { color: "\e[32m", prefix: "✓ " },
      warning: { color: "\e[33m", prefix: "⚠ " },
      error: { color: "\e[31m", prefix: "✗ " },
      info: { color: "\e[36m", prefix: "ℹ " },
      sovereign: { color: "\e[35m", prefix: "◆ " }
    }.freeze

    RESET = "\e[0m"

    # ─────────────────────────────────────────────────────────────────────────
    # DRAW - Main render method
    # ─────────────────────────────────────────────────────────────────────────
    def self.draw(mode, message, dock: 'MAIN', owner: 'sovereign')
      mode_config = MODES[mode] || MODES[:normal]
      timestamp = Time.now.strftime("%H:%M:%S")

      # Header with genesis mark
      puts
      puts "  #{DOUBLE_BAR * (WIDTH - 4)}"
      puts "  Newton".ljust(WIDTH - 12) + timestamp
      puts "  [Flash-3 Instantiated // 50s]"  # THE GENESIS MARK
      puts "  #{BAR * (WIDTH - 4)}"

      # Dock indicator
      puts "  DOCK: #{dock.upcase}".ljust(WIDTH - 16) + "OWNER: #{owner}"
      puts "  #{BAR * (WIDTH - 4)}"

      # Message
      puts
      puts "  #{mode_config[:color]}#{mode_config[:prefix]}#{message}#{RESET}"
      puts

      # Footer
      puts "  #{BAR * (WIDTH - 4)}"
      puts "  1 == 1".rjust(WIDTH - 4)
      puts "  #{DOUBLE_BAR * (WIDTH - 4)}"
      puts
    end

    # ─────────────────────────────────────────────────────────────────────────
    # BOOT SCREEN - System initialization display
    # ─────────────────────────────────────────────────────────────────────────
    def self.boot_screen
      os_info = NewtonOS.boot

      puts
      puts "  #{DOUBLE_BAR * (WIDTH - 4)}"
      puts
      puts "                    ███╗   ██╗███████╗██╗    ██╗████████╗ ██████╗ ███╗   ██╗"
      puts "                    ████╗  ██║██╔════╝██║    ██║╚══██╔══╝██╔═══██╗████╗  ██║"
      puts "                    ██╔██╗ ██║█████╗  ██║ █╗ ██║   ██║   ██║   ██║██╔██╗ ██║"
      puts "                    ██║╚██╗██║██╔══╝  ██║███╗██║   ██║   ██║   ██║██║╚██╗██║"
      puts "                    ██║ ╚████║███████╗╚███╔███╔╝   ██║   ╚██████╔╝██║ ╚████║"
      puts "                    ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝"
      puts
      puts "                              The State Machine for AI"
      puts
      puts "  #{BAR * (WIDTH - 4)}"
      puts
      puts "  KERNEL: #{os_info[:kernel]}".ljust(40) + "VERSION: #{os_info[:version]}"
      puts "  STATUS: #{os_info[:status].to_s.upcase}".ljust(40) + "INVARIANT: #{os_info[:invariant]}"
      puts
      puts "  #{BAR * (WIDTH - 4)}"
      puts "  GENESIS: Flash-3 Instantiated // 50 seconds // AI Studio"
      puts "  #{BAR * (WIDTH - 4)}"
      puts
      puts "  KNOWLEDGE DOMAINS:"
      os_info[:knowledge_domains].each do |domain|
        puts "    ◆ #{domain.to_s.upcase}"
      end
      puts
      puts "  #{DOUBLE_BAR * (WIDTH - 4)}"
      puts "  Jared Lewis | Ada Computing Company | Houston, Texas"
      puts "  #{DOUBLE_BAR * (WIDTH - 4)}"
      puts
    end

    # ─────────────────────────────────────────────────────────────────────────
    # GENESIS DISPLAY - Show the origin story
    # ─────────────────────────────────────────────────────────────────────────
    def self.genesis_display
      genesis = NewtonOS::Knowledge.genesis

      puts
      puts "  #{DOUBLE_BAR * (WIDTH - 4)}"
      puts "  GENESIS RECORD"
      puts "  #{BAR * (WIDTH - 4)}"
      puts
      puts "  EVENT:     #{genesis[:event]}"
      puts "  DURATION:  #{genesis[:duration]}"
      puts "  MODEL:     #{genesis[:model]}"
      puts "  PLATFORM:  #{genesis[:platform]}"
      puts "  ARCHITECT: #{genesis[:architect]}"
      puts
      puts "  FILES INSTANTIATED:"
      genesis[:files].each { |f| puts "    → #{f}" }
      puts
      puts "  #{BAR * (WIDTH - 4)}"
      puts "  MEANING:"
      puts "  #{genesis[:meaning]}"
      puts
      puts "  INVARIANT: #{genesis[:invariant]}"
      puts "  #{DOUBLE_BAR * (WIDTH - 4)}"
      puts
    end

    # ─────────────────────────────────────────────────────────────────────────
    # PROMPT - Interactive input
    # ─────────────────────────────────────────────────────────────────────────
    def self.prompt(dock: 'MAIN')
      print "  newton:#{dock.downcase}> "
      $stdin.gets&.strip
    end

    # ─────────────────────────────────────────────────────────────────────────
    # CLEAR - Reset display
    # ─────────────────────────────────────────────────────────────────────────
    def self.clear
      system('clear') || system('cls')
    end
  end

  # ─────────────────────────────────────────────────────────────────────────
  # TERMINAL - Interactive session
  # ─────────────────────────────────────────────────────────────────────────
  module Terminal
    def self.start
      PixelEngine.clear
      PixelEngine.boot_screen

      loop do
        input = PixelEngine.prompt(dock: 'MAIN')
        break if input.nil? || %w[exit quit q].include?(input.downcase)

        case input.downcase
        when 'genesis', 'origin', 'birth'
          PixelEngine.genesis_display
        when 'boot', 'status'
          PixelEngine.boot_screen
        when 'clear', 'cls'
          PixelEngine.clear
          PixelEngine.boot_screen
        when 'help', '?'
          show_help
        when ''
          # Do nothing for empty input
        else
          # Query the knowledge base
          result = NewtonOS::Knowledge.query(input)
          mode = result[:verified] ? :sovereign : :warning
          PixelEngine.draw(mode, result[:answer], dock: result[:domain].to_s.upcase)
        end
      end

      PixelEngine.draw(:info, "Session terminated. State preserved.", dock: 'EXIT')
    end

    def self.show_help
      PixelEngine.draw(:info, <<~HELP.strip, dock: 'HELP')
        COMMANDS:
          genesis   - Display origin story
          boot      - Show boot screen
          clear     - Clear terminal
          help      - This message
          exit      - End session

        ASK:
          "How was I made?"
          "Who built this?"
          "What is the invariant?"
      HELP
    end
  end
end

# ═══════════════════════════════════════════════════════════════════════════
# STANDALONE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

if __FILE__ == $0
  NewtonTahoe::Terminal.start
end
