/**
 * TinyTalk Runner
 *
 * Executes forges ONLY if verification returns fin.
 * Maintains blueprint instance state across calls.
 *
 * Pipeline: parse → compile laws → verify → execute (if fin) → record to ledger
 */

const { tokenize } = require('./tokenizer');
const { parse } = require('./parser');
const { Verifier, unwrap } = require('./verifier');
const { Ledger } = require('./ledger');

class BlueprintInstance {
  constructor(blueprintAST) {
    this.blueprint = blueprintAST;
    this.verifier = new Verifier(blueprintAST);
    this.state = { ...this.verifier.initialState };
    this.ledger = new Ledger(blueprintAST.name);
    this.history = [];
  }

  /**
   * Get current state (unwrapped for display)
   */
  getState() {
    const unwrapped = {};
    for (const [key, val] of Object.entries(this.state)) {
      if (typeof val === 'object' && val?.__type) {
        unwrapped[key] = { type: val.__type, value: val.value };
      } else {
        unwrapped[key] = val;
      }
    }
    return unwrapped;
  }

  /**
   * Get Ω (constraint space description)
   */
  getOmega() {
    return this.verifier.getOmega();
  }

  /**
   * Verify-only: check if a forge call would be admissible
   */
  verify(forgeName, args = {}) {
    return this.verifier.verifyForge(forgeName, this.state, args);
  }

  /**
   * Run a forge: verify first, then execute if fin
   */
  run(forgeName, args = {}) {
    const stateBefore = { ...this.state };
    const result = this.verifier.verifyForge(forgeName, this.state, args);

    if (result.status === 'fin') {
      // Apply the state changes
      this.state = result.newState;

      // Record to ledger
      const entry = this.ledger.record({
        forge: forgeName,
        args,
        stateBefore: this.snapshotState(stateBefore),
        stateAfter: this.snapshotState(this.state),
        status: 'fin',
        reply: result.reply,
        witness: null,
      });

      this.history.push({
        forge: forgeName,
        args,
        status: 'fin',
        reply: this.formatReply(result.reply),
        ledgerEntry: entry.hash,
      });

      return {
        status: 'fin',
        reply: this.formatReply(result.reply),
        state: this.getState(),
        ledgerEntry: entry,
        witness: null,
        violated_laws: [],
      };
    }

    // finfr — state does NOT change
    const entry = this.ledger.record({
      forge: forgeName,
      args,
      stateBefore: this.snapshotState(stateBefore),
      stateAfter: this.snapshotState(stateBefore), // unchanged
      status: 'finfr',
      reply: null,
      witness: result.witness,
    });

    this.history.push({
      forge: forgeName,
      args,
      status: 'finfr',
      reply: null,
      witness: result.witness,
      ledgerEntry: entry.hash,
    });

    return {
      status: 'finfr',
      reply: null,
      state: this.getState(),
      ledgerEntry: entry,
      witness: result.witness,
      violated_laws: result.violated_laws,
    };
  }

  /**
   * Reset state to initial
   */
  reset() {
    this.state = { ...this.verifier.initialState };
    this.ledger.record({
      forge: '<reset>',
      args: {},
      stateBefore: {},
      stateAfter: this.snapshotState(this.state),
      status: 'fin',
      reply: ':reset',
      witness: null,
    });
  }

  snapshotState(state) {
    const snapshot = {};
    for (const [key, val] of Object.entries(state)) {
      if (typeof val === 'object' && val?.__type) {
        snapshot[key] = { type: val.__type, value: val.value };
      } else {
        snapshot[key] = val;
      }
    }
    return snapshot;
  }

  formatReply(val) {
    if (val === null || val === undefined) return null;
    if (typeof val === 'object' && val.__type) {
      return `${val.__type}(${val.value})`;
    }
    if (typeof val === 'string' && val.startsWith(':')) {
      return val;
    }
    return val;
  }
}

// ── Runner: top-level orchestrator ─────────────────────
class Runner {
  constructor() {
    this.instances = new Map(); // name → BlueprintInstance
  }

  /**
   * Load source code: tokenize → parse → compile
   */
  load(source) {
    const { tokens, errors: tokenErrors } = tokenize(source);
    if (tokenErrors.length > 0) {
      return { success: false, errors: tokenErrors, ast: null, instances: [] };
    }

    const { ast, errors: parseErrors } = parse(tokens);

    // Create instances for each blueprint (even if there are parse warnings)
    const loaded = [];
    for (const bp of ast.blueprints) {
      const instance = new BlueprintInstance(bp);
      this.instances.set(bp.name, instance);
      loaded.push(bp.name);
    }

    // Fail only if no blueprints could be extracted
    if (loaded.length === 0 && parseErrors.length > 0) {
      return { success: false, errors: parseErrors, ast, instances: [] };
    }

    return {
      success: true,
      errors: parseErrors,
      ast,
      instances: loaded,
    };
  }

  /**
   * Run a forge on a named blueprint instance
   */
  run(blueprintName, forgeName, args = {}) {
    const instance = this.instances.get(blueprintName);
    if (!instance) {
      return {
        status: 'finfr',
        error: `Blueprint '${blueprintName}' not loaded`,
        reply: null,
        state: null,
        witness: { t_star: 'pre', x_star: {}, violated: [{ law: '<system>', reason: 'Blueprint not found' }], normal_hint: 'Load the blueprint first' },
        violated_laws: ['<system>'],
      };
    }
    return instance.run(forgeName, args);
  }

  /**
   * Verify-only (no state mutation)
   */
  verify(blueprintName, forgeName, args = {}) {
    const instance = this.instances.get(blueprintName);
    if (!instance) {
      return {
        status: 'finfr',
        error: `Blueprint '${blueprintName}' not loaded`,
        violated_laws: ['<system>'],
      };
    }
    return instance.verify(forgeName, args);
  }

  /**
   * Get current state of a blueprint instance
   */
  getState(blueprintName) {
    const instance = this.instances.get(blueprintName);
    if (!instance) return null;
    return instance.getState();
  }

  /**
   * Get Ω for a blueprint
   */
  getOmega(blueprintName) {
    const instance = this.instances.get(blueprintName);
    if (!instance) return null;
    return instance.getOmega();
  }

  /**
   * Get ledger for a blueprint
   */
  getLedger(blueprintName) {
    const instance = this.instances.get(blueprintName);
    if (!instance) return null;
    return instance.ledger.getEntries();
  }

  /**
   * Reset a blueprint instance
   */
  resetInstance(blueprintName) {
    const instance = this.instances.get(blueprintName);
    if (!instance) return false;
    instance.reset();
    return true;
  }

  /**
   * List all loaded blueprints
   */
  listBlueprints() {
    return Array.from(this.instances.keys());
  }
}

module.exports = { Runner, BlueprintInstance };
