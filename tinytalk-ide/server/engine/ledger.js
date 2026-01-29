/**
 * TinyTalk Ledger
 *
 * Append-only commit log for verified computations.
 * Each entry records: code hash, state before/after, fin/finfr, witness, timestamp.
 *
 * "Commit only if verified" — the whole point of the Sovereign Stack.
 */

const crypto = require('crypto');

class LedgerEntry {
  constructor(index, data, previousHash) {
    this.index = index;
    this.timestamp = new Date().toISOString();
    this.data = data;
    this.previousHash = previousHash;
    this.hash = this.computeHash();
  }

  computeHash() {
    const content = JSON.stringify({
      index: this.index,
      timestamp: this.timestamp,
      data: this.data,
      previousHash: this.previousHash,
    });
    return crypto.createHash('sha256').update(content).digest('hex').slice(0, 16);
  }

  toJSON() {
    return {
      index: this.index,
      timestamp: this.timestamp,
      hash: this.hash,
      previousHash: this.previousHash,
      forge: this.data.forge,
      args: this.data.args,
      status: this.data.status,
      reply: this.data.reply,
      stateBefore: this.data.stateBefore,
      stateAfter: this.data.stateAfter,
      witness: this.data.witness,
    };
  }
}

class Ledger {
  constructor(blueprintName) {
    this.blueprintName = blueprintName;
    this.entries = [];
    this.currentHash = '0000000000000000'; // genesis

    // Record genesis entry
    this.record({
      forge: '<genesis>',
      args: {},
      stateBefore: null,
      stateAfter: null,
      status: 'fin',
      reply: null,
      witness: null,
    });
  }

  /**
   * Append a new entry to the ledger (append-only)
   */
  record(data) {
    const entry = new LedgerEntry(
      this.entries.length,
      data,
      this.currentHash
    );
    this.entries.push(entry);
    this.currentHash = entry.hash;
    return entry;
  }

  /**
   * Get all entries
   */
  getEntries() {
    return this.entries.map(e => e.toJSON());
  }

  /**
   * Get entry by index
   */
  getEntry(index) {
    if (index < 0 || index >= this.entries.length) return null;
    return this.entries[index].toJSON();
  }

  /**
   * Verify chain integrity (each entry's previousHash matches)
   */
  verifyChain() {
    for (let i = 1; i < this.entries.length; i++) {
      if (this.entries[i].previousHash !== this.entries[i - 1].hash) {
        return {
          valid: false,
          brokenAt: i,
          reason: `Entry ${i} previousHash doesn't match entry ${i - 1} hash`,
        };
      }
      // Re-compute hash to check integrity
      const recomputed = this.entries[i].computeHash();
      if (recomputed !== this.entries[i].hash) {
        return {
          valid: false,
          brokenAt: i,
          reason: `Entry ${i} hash mismatch (tampered)`,
        };
      }
    }
    return { valid: true, length: this.entries.length };
  }

  /**
   * Replay: re-execute the ledger from genesis to verify reproducibility
   */
  getReplayData() {
    return this.entries
      .filter(e => e.data.forge !== '<genesis>')
      .map(e => ({
        forge: e.data.forge,
        args: e.data.args,
        expectedStatus: e.data.status,
        expectedReply: e.data.reply,
      }));
  }

  /**
   * Summary: fin/finfr counts
   */
  getSummary() {
    let finCount = 0;
    let finfrCount = 0;

    for (const entry of this.entries) {
      if (entry.data.status === 'fin') finCount++;
      if (entry.data.status === 'finfr') finfrCount++;
    }

    return {
      blueprint: this.blueprintName,
      totalEntries: this.entries.length,
      fin: finCount,
      finfr: finfrCount,
      currentHash: this.currentHash,
      chainValid: this.verifyChain().valid,
    };
  }
}

module.exports = { Ledger, LedgerEntry };
