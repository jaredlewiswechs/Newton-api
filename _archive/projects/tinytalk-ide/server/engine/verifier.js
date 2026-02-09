/**
 * Newton Verifier
 *
 * Compiles laws into predicates and checks:
 *   (a) snapshot state ∈ Ω
 *   (b) proposed forge transition stays admissible
 *
 * Returns fin (admissible) or finfr (forbidden) with a witness.
 *
 * Ω = { x ∈ S : ∀ c ∈ C, c(x) = true }
 */

const { NodeType } = require('./parser');

// ── Witness Structure ──────────────────────────────────
// W = (t*, x*, I*, n*)
// t*: first failure time/state
// x*: state snapshot at failure
// I*: violated constraints (law names)
// n*: repair normal hint
class Witness {
  constructor(tStar, xStar, violated, normalHint) {
    this.t_star = tStar;         // which step failed (or 'pre' for law check)
    this.x_star = xStar;         // state snapshot at failure
    this.violated = violated;     // array of {law, clause, reason}
    this.normal_hint = normalHint; // suggested repair direction
  }

  toJSON() {
    return {
      t_star: this.t_star,
      x_star: this.x_star,
      violated: this.violated,
      normal_hint: this.normal_hint,
    };
  }
}

// ── Compiled Law ───────────────────────────────────────
class CompiledLaw {
  constructor(name, predicate, outcome, clauses, line) {
    this.name = name;
    this.predicate = predicate;  // (state, request) => boolean (true = condition met)
    this.outcome = outcome;       // 'fin' or 'finfr'
    this.clauses = clauses;       // original clause descriptions
    this.line = line;
  }
}

// ── Expression Evaluator ───────────────────────────────
function evaluateExpr(node, state, locals) {
  if (!node) return undefined;

  switch (node.type) {
    case NodeType.NUMBER_LIT:
      return node.value;

    case NodeType.STRING_LIT:
      return node.value;

    case NodeType.SYMBOL_LIT:
      return `:${node.value}`;

    case NodeType.FIELD_REF:
      return state[`@${node.name}`];

    case NodeType.IDENTIFIER:
      if (locals && locals[node.name] !== undefined) return locals[node.name];
      if (state[node.name] !== undefined) return state[node.name];
      return undefined;

    case NodeType.TYPE_CONSTRUCT: {
      const arg = evaluateExpr(node.argument, state, locals);
      // Type constructors wrap the value with type info
      return { __type: node.typeName, value: typeof arg === 'object' && arg?.__type ? arg.value : arg };
    }

    case NodeType.BINARY_EXPR: {
      const left = evaluateExpr(node.left, state, locals);
      const right = evaluateExpr(node.right, state, locals);
      const lv = unwrap(left);
      const rv = unwrap(right);

      switch (node.operator) {
        case '+': return wrapResult(left, right, lv + rv);
        case '-': return wrapResult(left, right, lv - rv);
        case '*': return wrapResult(left, right, lv * rv);
        case '/':
          if (rv === 0) return { __type: 'Error', value: 'division_by_zero' };
          return wrapResult(left, right, lv / rv);
        default: return undefined;
      }
    }

    case NodeType.UNARY_EXPR: {
      const operand = evaluateExpr(node.operand, state, locals);
      if (node.operator === '-') {
        const v = unwrap(operand);
        return typeof operand === 'object' && operand?.__type
          ? { __type: operand.__type, value: -v }
          : -v;
      }
      return undefined;
    }

    case NodeType.GROUP_EXPR:
      return evaluateExpr(node.expression, state, locals);

    case NodeType.FUNC_CALL: {
      const args = node.args.map(a => evaluateExpr(a, state, locals));
      // Built-in functions
      switch (node.name) {
        case 'ratio': {
          const f = unwrap(args[0]);
          const g = unwrap(args[1]);
          if (g === 0) return { __type: 'Error', value: 'ratio_undefined' };
          return f / g;
        }
        case 'finfr_if_undefined': {
          const f = unwrap(args[0]);
          const g = unwrap(args[1]);
          if (g === 0 || g === undefined) return ':finfr';
          return f / g;
        }
        case 'abs':
          return Math.abs(unwrap(args[0]));
        case 'sqrt': {
          const v = unwrap(args[0]);
          if (v < 0) return { __type: 'Error', value: 'sqrt_negative' };
          return Math.sqrt(v);
        }
        case 'as_real': {
          const v = unwrap(args[0]);
          return { __type: 'Real', value: v };
        }
        default:
          return undefined;
      }
    }

    default:
      return undefined;
  }
}

function unwrap(val) {
  if (typeof val === 'object' && val !== null && val.__type) {
    return val.value;
  }
  return val;
}

function wrapResult(left, right, value) {
  // Preserve type from left operand if typed
  if (typeof left === 'object' && left?.__type) {
    return { __type: left.__type, value };
  }
  if (typeof right === 'object' && right?.__type) {
    return { __type: right.__type, value };
  }
  return value;
}

// ── Condition Evaluator ────────────────────────────────
function evaluateCondition(condition, state, request) {
  if (!condition) return false;

  switch (condition.type) {
    case NodeType.REQUEST_IS:
      return request === `:${condition.symbol}`;

    case NodeType.COMPARISON: {
      const left = evaluateExpr(condition.left, state);
      const right = evaluateExpr(condition.right, state);
      const lv = unwrap(left);
      const rv = unwrap(right);

      switch (condition.operator) {
        case '<': return lv < rv;
        case '<=': return lv <= rv;
        case '>': return lv > rv;
        case '>=': return lv >= rv;
        case '==': return lv === rv;
        case '!=': return lv !== rv;
        default: return false;
      }
    }

    default:
      return false;
  }
}

// ── Law Compiler ───────────────────────────────────────
function compileLaw(lawNode) {
  const clauses = lawNode.clauses.map(clause => {
    const condition = clause.condition;
    return {
      type: clause.type,
      description: describeCondition(condition),
      condition,
    };
  });

  const outcome = lawNode.outcome ? lawNode.outcome.type : NodeType.FINFR;

  // The predicate: returns true if ALL when/and conditions are met
  // (meaning this law "fires" — and the outcome applies)
  const predicate = (state, request) => {
    return clauses.every(clause => {
      return evaluateCondition(clause.condition, state, request);
    });
  };

  return new CompiledLaw(
    lawNode.name,
    predicate,
    outcome === NodeType.FINFR ? 'finfr' : 'fin',
    clauses.map(c => c.description),
    lawNode.line
  );
}

function describeCondition(condition) {
  if (!condition) return '<empty>';

  switch (condition.type) {
    case NodeType.REQUEST_IS:
      return `request is :${condition.symbol}`;
    case NodeType.COMPARISON:
      return `${describeExpr(condition.left)} ${condition.operator} ${describeExpr(condition.right)}`;
    default:
      return '<condition>';
  }
}

function describeExpr(node) {
  if (!node) return '?';
  switch (node.type) {
    case NodeType.FIELD_REF: return `@${node.name}`;
    case NodeType.IDENTIFIER: return node.name;
    case NodeType.NUMBER_LIT: return String(node.value);
    case NodeType.TYPE_CONSTRUCT: return `${node.typeName}(${describeExpr(node.argument)})`;
    case NodeType.BINARY_EXPR: return `(${describeExpr(node.left)} ${node.operator} ${describeExpr(node.right)})`;
    case NodeType.UNARY_EXPR: return `(-${describeExpr(node.operand)})`;
    default: return '<expr>';
  }
}

// ── Verifier ───────────────────────────────────────────
class Verifier {
  constructor(blueprintAST) {
    this.blueprint = blueprintAST;
    this.compiledLaws = blueprintAST.laws.map(compileLaw);

    // Build initial state from field declarations
    this.initialState = {};
    for (const field of blueprintAST.fields) {
      this.initialState[`@${field.name}`] = { __type: field.fieldType, value: 0 };
    }
  }

  /**
   * Verify state membership in Ω.
   * Ω = { x ∈ S : no finfr law fires }
   *
   * @param {Object} state - current state snapshot
   * @param {string|null} request - current request symbol (e.g. ':mean')
   * @returns {{ status: 'fin'|'finfr', witness: Witness|null, violated_laws: string[] }}
   */
  verifyState(state, request = null) {
    const violations = [];

    for (const law of this.compiledLaws) {
      if (law.outcome === 'finfr' && law.predicate(state, request)) {
        violations.push({
          law: law.name,
          clauses: law.clauses,
          reason: `Law '${law.name}' fires → finfr`,
          line: law.line,
        });
      }
    }

    if (violations.length > 0) {
      const witness = new Witness(
        'pre',
        { ...state },
        violations,
        this.computeRepairHint(violations, state)
      );

      return {
        status: 'finfr',
        witness: witness.toJSON(),
        violated_laws: violations.map(v => v.law),
      };
    }

    return {
      status: 'fin',
      witness: null,
      violated_laws: [],
    };
  }

  /**
   * Verify a forge transition.
   * Checks:
   *   1. Laws pass BEFORE execution (pre-check with request)
   *   2. Laws pass AFTER execution (post-check without request)
   *
   * @param {string} forgeName
   * @param {Object} state
   * @param {Object} args - named arguments
   * @returns {{ status, witness, violated_laws, newState, reply }}
   */
  verifyForge(forgeName, state, args = {}) {
    const forgeNode = this.blueprint.forges.find(f => f.name === forgeName);
    if (!forgeNode) {
      return {
        status: 'finfr',
        witness: new Witness('pre', state, [{
          law: '<system>',
          clauses: [],
          reason: `Forge '${forgeName}' not found`,
        }], 'Define the forge').toJSON(),
        violated_laws: ['<system>'],
        newState: state,
        reply: null,
      };
    }

    // Determine request symbol from forge body
    const request = this.extractRequest(forgeNode);

    // Pre-check: verify laws with request context
    const preCheck = this.verifyState(state, request);
    if (preCheck.status === 'finfr') {
      return {
        ...preCheck,
        newState: state,
        reply: null,
      };
    }

    // Simulate execution
    const { newState, reply, error } = this.simulateForge(forgeNode, state, args);

    if (error) {
      return {
        status: 'finfr',
        witness: new Witness('exec', state, [{
          law: '<runtime>',
          clauses: [],
          reason: error,
        }], 'Fix the expression').toJSON(),
        violated_laws: ['<runtime>'],
        newState: state,
        reply: null,
      };
    }

    // Post-check: verify laws after mutation (without request context)
    const postCheck = this.verifyState(newState, null);
    if (postCheck.status === 'finfr') {
      return {
        status: 'finfr',
        witness: new Witness('post', newState, postCheck.witness.violated, 'Revert mutation').toJSON(),
        violated_laws: postCheck.violated_laws,
        newState: state, // Revert to original state
        reply: null,
      };
    }

    return {
      status: 'fin',
      witness: null,
      violated_laws: [],
      newState,
      reply,
    };
  }

  /**
   * Extract request symbol from forge body (looks for `request = :symbol`)
   */
  extractRequest(forgeNode) {
    for (const stmt of forgeNode.body) {
      if (stmt.type === NodeType.REQUEST_SET) {
        return `:${stmt.symbol}`;
      }
    }
    return null;
  }

  /**
   * Simulate forge execution (dry run to compute new state + reply)
   */
  simulateForge(forgeNode, state, args) {
    const newState = { ...state };
    const locals = {};
    let reply = null;

    // Bind parameters
    for (let i = 0; i < forgeNode.params.length; i++) {
      const param = forgeNode.params[i];
      const argValue = args[param.name];
      if (argValue !== undefined) {
        locals[param.name] = param.paramType
          ? { __type: param.paramType, value: argValue }
          : argValue;
      }
    }

    // Execute body statements
    for (const stmt of forgeNode.body) {
      try {
        switch (stmt.type) {
          case NodeType.ASSIGNMENT: {
            const val = evaluateExpr(stmt.value, newState, locals);
            if (val && val.__type === 'Error') {
              return { newState: state, reply: null, error: `Runtime error: ${val.value}` };
            }
            newState[`@${stmt.field}`] = val;
            break;
          }
          case NodeType.LOCAL_DEF: {
            const val = evaluateExpr(stmt.value, newState, locals);
            if (val && val.__type === 'Error') {
              return { newState: state, reply: null, error: `Runtime error: ${val.value}` };
            }
            locals[stmt.name] = val;
            break;
          }
          case NodeType.REPLY: {
            reply = evaluateExpr(stmt.value, newState, locals);
            if (reply && reply.__type === 'Error') {
              return { newState: state, reply: null, error: `Runtime error: ${reply.value}` };
            }
            break;
          }
          case NodeType.REQUEST_SET:
            // Already handled in extractRequest
            break;
          default:
            // Expression statement — evaluate for side effects
            evaluateExpr(stmt, newState, locals);
        }
      } catch (err) {
        return { newState: state, reply: null, error: err.message };
      }
    }

    return { newState, reply, error: null };
  }

  /**
   * Compute a repair hint from violations
   */
  computeRepairHint(violations, state) {
    const hints = violations.map(v => {
      if (v.law === 'NoDivideByZero' || v.law.includes('DivideByZero')) {
        return 'Ensure denominator > 0 before division';
      }
      if (v.law.includes('NeedsTwoSamples') || v.law.includes('NeedsTwo')) {
        return 'Add more samples before computing this statistic';
      }
      if (v.law.includes('NonNegative')) {
        return 'Value must be >= 0';
      }
      return `Satisfy law '${v.law}' before proceeding`;
    });
    return hints.join('; ');
  }

  /**
   * Get the Ω description (set of constraints)
   */
  getOmega() {
    return this.compiledLaws.map(law => ({
      name: law.name,
      outcome: law.outcome,
      clauses: law.clauses,
      description: `When ${law.clauses.join(' AND ')} → ${law.outcome}`,
    }));
  }
}

module.exports = { Verifier, Witness, evaluateExpr, unwrap };
