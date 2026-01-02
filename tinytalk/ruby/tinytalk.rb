# frozen_string_literal: true

# ═══════════════════════════════════════════════════════════════════════════════
#  tinyTalk for Ruby
# ═══════════════════════════════════════════════════════════════════════════════
#
# The "No-First" constraint language. Define what cannot happen.
#
# Usage:
#   require_relative 'tinytalk'
#   include TinyTalk
#
#   class RiskGovernor < Blueprint
#     field :assets, Money, default: Money.new(1000)
#     field :liabilities, Money, default: Money.new(0)
#
#     law :insolvency do
#       when_condition(liabilities > assets) { finfr }
#     end
#
#     forge :execute_trade do |amount|
#       self.liabilities = liabilities + amount
#       :cleared
#     end
#   end

module TinyTalk
  VERSION = "1.0.0"

  # ═══════════════════════════════════════════════════════════════════════════
  # BOOK I: THE LEXICON
  # ═══════════════════════════════════════════════════════════════════════════

  # Finality. Ontological death. The state cannot exist.
  class Finfr < StandardError
    attr_reader :law_name

    def initialize(law_name = "unknown", message = nil)
      @law_name = law_name
      super(message || "Law '#{law_name}' prevents this state (finfr)")
    end
  end

  # Closure. A stopping point that can be reopened.
  class Fin < StandardError
    attr_reader :law_name

    def initialize(law_name = "unknown", message = nil)
      @law_name = law_name
      super(message || "Law '#{law_name}' closed this path (fin)")
    end
  end

  # Sentinel for finfr
  FINFR = :finfr
  # Sentinel for fin
  FIN = :fin

  # Declares a fact. Returns result if condition is true.
  def when_condition(condition, &block)
    return unless condition
    result = block&.call
    case result
    when :finfr, FINFR
      raise Finfr.new("inline")
    when :fin, FIN
      raise Fin.new("inline")
    end
    result
  end

  def finfr
    FINFR
  end

  def fin
    FIN
  end

  # ═══════════════════════════════════════════════════════════════════════════
  # BOOK II: MATTER - Typed Values
  # ═══════════════════════════════════════════════════════════════════════════

  class Matter
    attr_reader :value, :unit

    def initialize(value, unit = nil)
      @value = value.to_f
      @unit = unit || self.class.default_unit
    end

    def self.default_unit
      ""
    end

    def +(other)
      ensure_same_type!(other)
      self.class.new(@value + other.value)
    end

    def -(other)
      ensure_same_type!(other)
      self.class.new(@value - other.value)
    end

    def *(other)
      if other.is_a?(Numeric)
        self.class.new(@value * other)
      else
        raise TypeError, "Cannot multiply #{self.class} by #{other.class}"
      end
    end

    def /(other)
      if other.is_a?(Numeric)
        self.class.new(@value / other)
      elsif other.is_a?(self.class)
        @value / other.value  # Returns scalar
      else
        raise TypeError, "Cannot divide #{self.class} by #{other.class}"
      end
    end

    def <(other)
      ensure_same_type!(other)
      @value < other.value
    end

    def >(other)
      ensure_same_type!(other)
      @value > other.value
    end

    def <=(other)
      ensure_same_type!(other)
      @value <= other.value
    end

    def >=(other)
      ensure_same_type!(other)
      @value >= other.value
    end

    def ==(other)
      return false unless other.is_a?(self.class)
      @value == other.value
    end

    def to_s
      "#{@value} #{@unit}"
    end

    def inspect
      "#{self.class}(#{@value})"
    end

    private

    def ensure_same_type!(other)
      unless other.is_a?(self.class)
        raise TypeError, "Cannot operate on #{self.class} with #{other.class}"
      end
    end
  end

  class Money < Matter
    def self.default_unit
      "USD"
    end
  end

  class Mass < Matter
    def self.default_unit
      "kg"
    end
  end

  class Distance < Matter
    def self.default_unit
      "m"
    end
  end

  class Temperature < Matter
    def self.default_unit
      "C"
    end

    def to_celsius
      case @unit
      when "C" then self
      when "F" then Temperature.new((@value - 32) * 5.0 / 9.0, "C")
      when "K" then Temperature.new(@value - 273.15, "C")
      else self
      end
    end

    def to_fahrenheit
      case @unit
      when "F" then self
      when "C" then Temperature.new(@value * 9.0 / 5.0 + 32, "F")
      when "K" then Temperature.new((@value - 273.15) * 9.0 / 5.0 + 32, "F")
      else self
      end
    end
  end

  class Pressure < Matter
    def self.default_unit
      "PSI"
    end
  end

  class Volume < Matter
    def self.default_unit
      "L"
    end
  end

  # Convenience constructors
  def self.Celsius(value)
    Temperature.new(value, "C")
  end

  def self.Fahrenheit(value)
    Temperature.new(value, "F")
  end

  def self.PSI(value)
    Pressure.new(value, "PSI")
  end

  def self.Meters(value)
    Distance.new(value, "m")
  end

  def self.Kilograms(value)
    Mass.new(value, "kg")
  end

  def self.Liters(value)
    Volume.new(value, "L")
  end

  # ═══════════════════════════════════════════════════════════════════════════
  # BOOK III: THE BLUEPRINT
  # ═══════════════════════════════════════════════════════════════════════════

  class Law
    attr_reader :name, :block

    def initialize(name, &block)
      @name = name
      @block = block
    end

    def evaluate(context)
      context.instance_eval(&@block)
      false  # No exception = not triggered
    rescue Finfr, Fin
      true   # Exception = triggered
    end
  end

  class Blueprint
    class << self
      def fields
        @fields ||= {}
      end

      def laws
        @laws ||= []
      end

      def forges
        @forges ||= {}
      end

      def field(name, type = Object, default: nil)
        fields[name] = { type: type, default: default }

        # Define getter
        define_method(name) do
          instance_variable_get("@#{name}") || self.class.fields[name][:default]
        end

        # Define setter
        define_method("#{name}=") do |value|
          instance_variable_set("@#{name}", value)
        end
      end

      def law(name, &block)
        laws << Law.new(name, &block)
      end

      def forge(name, &block)
        forges[name] = block

        define_method(name) do |*args|
          # Save state for rollback
          saved_state = save_state

          begin
            # Execute the forge
            result = instance_exec(*args, &self.class.forges[name])

            # Check all laws
            self.class.laws.each do |law|
              if law.evaluate(self)
                restore_state(saved_state)
                raise Finfr.new(law.name)
              end
            end

            result
          rescue Finfr, Fin
            restore_state(saved_state)
            raise
          rescue => e
            restore_state(saved_state)
            raise
          end
        end
      end

      def inherited(subclass)
        # Copy fields and laws to subclass
        subclass.instance_variable_set(:@fields, fields.dup)
        subclass.instance_variable_set(:@laws, laws.dup)
        subclass.instance_variable_set(:@forges, forges.dup)
      end
    end

    def initialize(**kwargs)
      self.class.fields.each do |name, config|
        value = kwargs.fetch(name, config[:default])
        instance_variable_set("@#{name}", value)
      end
    end

    def save_state
      state = {}
      self.class.fields.each_key do |name|
        value = instance_variable_get("@#{name}")
        state[name] = value.respond_to?(:dup) ? value.dup : value
      end
      state
    end

    def restore_state(state)
      state.each do |name, value|
        instance_variable_set("@#{name}", value)
      end
    end

    def get_state
      state = {}
      self.class.fields.each_key do |name|
        state[name] = instance_variable_get("@#{name}")
      end
      state
    end

    def to_s
      fields_str = get_state.map { |k, v| "#{k}=#{v.inspect}" }.join(", ")
      "#{self.class.name}(#{fields_str})"
    end

    def inspect
      to_s
    end
  end

  # ═══════════════════════════════════════════════════════════════════════════
  # BOOK IV: THE ENGINE
  # ═══════════════════════════════════════════════════════════════════════════

  class Presence
    attr_reader :state, :timestamp, :label

    def initialize(state, timestamp: nil, label: "")
      @state = state.dup
      @timestamp = timestamp
      @label = label
    end

    def -(other)
      Delta.from_presences(other, self)
    end

    def to_s
      "Presence(#{@state}, label='#{@label}')"
    end
  end

  class Delta
    attr_reader :changes, :source, :target

    def initialize(changes, source: nil, target: nil)
      @changes = changes
      @source = source
      @target = target
    end

    def self.from_presences(start_p, end_p)
      changes = {}

      all_keys = (start_p.state.keys + end_p.state.keys).uniq

      all_keys.each do |key|
        start_val = start_p.state[key]
        end_val = end_p.state[key]

        next if start_val == end_val

        if start_val.is_a?(Numeric) && end_val.is_a?(Numeric)
          changes[key] = {
            from: start_val,
            to: end_val,
            delta: end_val - start_val
          }
        else
          changes[key] = {
            from: start_val,
            to: end_val,
            delta: nil
          }
        end
      end

      new(changes, source: start_p, target: end_p)
    end

    def to_s
      "Delta(#{@changes})"
    end
  end

  class KineticEngine < Blueprint
    field :presence_start, Presence
    field :presence_end, Presence
    field :kinetic_delta, Delta

    def initialize(**kwargs)
      super
      @boundary_checks = []
    end

    def add_boundary(name = "", &block)
      @boundary_checks << { name: name, check: block }
    end

    def resolve_motion(start_p, end_p, signal: nil)
      @presence_start = start_p
      @presence_end = end_p
      @kinetic_delta = end_p - start_p

      # Check boundaries
      @boundary_checks.each do |boundary|
        if boundary[:check].call(@kinetic_delta)
          return {
            status: :finfr,
            reason: "Boundary '#{boundary[:name]}' violated",
            message: "ONTO DEATH: This motion cannot exist.",
            delta: @kinetic_delta.changes
          }
        end
      end

      {
        status: :synchronized,
        delta: @kinetic_delta.changes,
        from: start_p.state,
        to: end_p.state
      }
    end
  end
end
