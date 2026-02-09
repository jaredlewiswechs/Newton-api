# ============================================================================
#  Newton HTTP Client
# ============================================================================
#
#  R6 client for Newton constraint verification API.
#  Combinations over permutations: verify constraint SPACES, not enumerate.
#
# ============================================================================

#' @importFrom httr2 request req_headers req_body_json req_perform resp_body_json resp_status
#' @importFrom jsonlite toJSON fromJSON
#' @importFrom R6 R6Class
NULL

#' Newton API Client
#'
#' @description
#' R6 class providing interface to Newton constraint verification API.
#' Newton inverts computing: verification IS the computation.
#'
#' @details
#' The client provides methods for:
#' - Content verification against safety constraints
#' - Verified mathematical computation
#' - CDL constraint evaluation
#' - Encrypted vault storage
#' - Immutable ledger access
#'
#' @examples
#' \dontrun{
#' # Create client
#' client <- Newton$new("http://localhost:8000", api_key = "your-key")
#'
#' # Check health
#' client$health()
#'
#' # Verify content
#' result <- client$verify("Hello world", categories = c("harm", "medical"))
#'
#' # Verified calculation
#' result <- client$calculate("2 + 2")
#'
#' # CDL constraint
#' result <- client$constraint(
#'   constraint = list(field = "balance", operator = "ge", value = 0),
#'   object = list(balance = 100)
#' )
#' }
#'
#' @export
Newton <- R6::R6Class(
  "Newton",

  public = list(

    #' @field base_url Base URL of Newton API
    base_url = NULL,

    #' @field api_key API key for authentication
    api_key = NULL,

    #' @field timeout Request timeout in seconds
    timeout = NULL,

    #' @description
    #' Create a new Newton client
    #' @param base_url Base URL of Newton API (default: "http://localhost:8000")
    #' @param api_key API key for authentication (optional)
    #' @param timeout Request timeout in seconds (default: 30)
    #' @return A new Newton client instance
    initialize = function(base_url = "http://localhost:8000",
                          api_key = NULL,
                          timeout = 30) {
      self$base_url <- sub("/$", "", base_url)  # Remove trailing slash
      self$api_key <- api_key
      self$timeout <- timeout
    },

    #' @description
    #' Make HTTP request to Newton API
    #' @param method HTTP method ("GET" or "POST")
    #' @param endpoint API endpoint
    #' @param data Request body data (for POST)
    #' @param params Query parameters (for GET)
    #' @return Parsed response
    request = function(method, endpoint, data = NULL, params = NULL) {
      url <- paste0(self$base_url, endpoint)

      # Build request
      req <- httr2::request(url)

      # Add headers
      headers <- list("Content-Type" = "application/json")
      if (!is.null(self$api_key)) {
        headers[["X-API-Key"]] <- self$api_key
      }
      req <- httr2::req_headers(req, !!!headers)

      # Add timeout
      req <- httr2::req_timeout(req, self$timeout)

      # Add body for POST
      if (method == "POST" && !is.null(data)) {
        req <- httr2::req_body_json(req, data)
      }

      # Add query params for GET
      if (method == "GET" && !is.null(params)) {
        req <- httr2::req_url_query(req, !!!params)
      }

      # Set method
      req <- httr2::req_method(req, method)

      # Perform request
      tryCatch({
        resp <- httr2::req_perform(req)
        status <- httr2::resp_status(resp)

        if (status >= 400) {
          stop(paste("Newton API error:", status))
        }

        httr2::resp_body_json(resp)
      }, error = function(e) {
        stop(paste("Newton request failed:", e$message))
      })
    },

    # ========================================================================
    #  CORE ENDPOINTS
    # ========================================================================

    #' @description
    #' Check API health status
    #' @return Health status response
    health = function() {
      self$request("GET", "/health")
    },

    #' @description
    #' Verify content against safety constraints
    #'
    #' Combinations over permutations: checks if content falls within

    #' the valid constraint space, not all possible violations.
    #'
    #' @param content Content to verify
    #' @param categories Constraint categories (default: all four)
    #' @return Verification result with passed/failed constraints
    verify = function(content,
                      categories = c("harm", "medical", "legal", "security")) {
      self$request("POST", "/verify", list(
        content = content,
        categories = categories
      ))
    },

    #' @description
    #' Perform verified mathematical computation
    #'
    #' All computation is deterministic and auditable.
    #' Same input always yields same output.
    #'
    #' @param expression Mathematical expression to evaluate
    #' @param variables Named list of variable values
    #' @return Computation result
    calculate = function(expression, variables = list()) {
      self$request("POST", "/calculate", list(
        expression = expression,
        variables = variables
      ))
    },

    #' @description
    #' Evaluate CDL constraint against object
    #'
    #' The core verification primitive. Constraints define the
    #' valid state space; objects either fall within or without.
    #'
    #' @param constraint CDL constraint specification
    #' @param object Object to verify against constraint
    #' @return Constraint evaluation result
    constraint = function(constraint, object) {
      self$request("POST", "/constraint", list(
        constraint = constraint,
        object = object
      ))
    },

    #' @description
    #' Verify fact against external ground truth
    #' @param claim Claim to verify
    #' @param sources Sources to check against
    #' @return Grounding verification result
    ground = function(claim, sources = list()) {
      self$request("POST", "/ground", list(
        claim = claim,
        sources = sources
      ))
    },

    #' @description
    #' Perform robust statistical analysis
    #' @param data Numeric vector of data
    #' @param methods Statistical methods to apply
    #' @return Statistical analysis results
    statistics = function(data, methods = c("mad", "iqr", "zscore")) {
      self$request("POST", "/statistics", list(
        data = data,
        methods = methods
      ))
    },

    #' @description
    #' Full verification pipeline
    #' @param query Query to process
    #' @param context Additional context
    #' @return Full verification result
    ask = function(query, context = list()) {
      self$request("POST", "/ask", list(
        query = query,
        context = context
      ))
    },

    # ========================================================================
    #  VAULT ENDPOINTS (Encrypted Storage)
    # ========================================================================

    #' @description
    #' Store data in encrypted vault
    #' @param key Storage key
    #' @param value Value to store
    #' @param ttl Time-to-live in seconds (optional)
    #' @return Storage confirmation
    vault_store = function(key, value, ttl = NULL) {
      data <- list(key = key, value = value)
      if (!is.null(ttl)) {
        data$ttl <- ttl
      }
      self$request("POST", "/vault/store", data)
    },

    #' @description
    #' Retrieve data from encrypted vault
    #' @param key Storage key
    #' @return Retrieved value
    vault_retrieve = function(key) {
      self$request("POST", "/vault/retrieve", list(key = key))
    },

    # ========================================================================
    #  LEDGER ENDPOINTS (Immutable Audit Trail)
    # ========================================================================

    #' @description
    #' Get ledger entries
    #' @param limit Maximum entries to return
    #' @param offset Offset for pagination
    #' @return Ledger entries
    ledger = function(limit = 100, offset = 0) {
      self$request("GET", "/ledger", params = list(
        limit = limit,
        offset = offset
      ))
    },

    #' @description
    #' Get specific ledger entry
    #' @param entry_id Entry ID or fingerprint
    #' @return Ledger entry
    ledger_entry = function(entry_id) {
      self$request("GET", paste0("/ledger/", entry_id))
    },

    # ========================================================================
    #  RATIO CONSTRAINTS (f/g Analysis)
    # ========================================================================

    #' @description
    #' Evaluate ratio constraint (f/g analysis)
    #'
    #' Core to Newton's philosophy: every constraint is a ratio.
    #' f = what you're trying to do (forge/fact/function)
    #' g = what reality allows (ground/goal/governance)
    #'
    #' When f/g > threshold or g = 0, state cannot exist (finfr).
    #'

    #' @param f_field Field name for numerator
    #' @param g_field Field name for denominator
    #' @param operator Comparison operator ("lt", "le", "gt", "ge", "eq")
    #' @param threshold Threshold value
    #' @param object Object containing f and g values
    #' @return Ratio constraint evaluation
    ratio_check = function(f_field, g_field, operator, threshold, object) {
      constraint <- list(
        type = "ratio",
        f_field = f_field,
        g_field = g_field,
        operator = paste0("ratio_", operator),
        threshold = threshold
      )
      self$request("POST", "/constraint", list(
        constraint = constraint,
        object = object
      ))
    },

    # ========================================================================
    #  CONVENIENCE METHODS
    # ========================================================================

    #' @description
    #' Verified addition
    #' @param a First operand
    #' @param b Second operand
    #' @return Sum
    add = function(a, b) {
      result <- self$calculate(paste0(a, " + ", b))
      result$result
    },

    #' @description
    #' Verified subtraction
    #' @param a First operand
    #' @param b Second operand
    #' @return Difference
    subtract = function(a, b) {
      result <- self$calculate(paste0(a, " - ", b))
      result$result
    },

    #' @description
    #' Verified multiplication
    #' @param a First operand
    #' @param b Second operand
    #' @return Product
    multiply = function(a, b) {
      result <- self$calculate(paste0(a, " * ", b))
      result$result
    },

    #' @description
    #' Verified division
    #' @param a Numerator
    #' @param b Denominator
    #' @return Quotient (or error if b = 0)
    divide = function(a, b) {
      result <- self$calculate(paste0(a, " / ", b))
      result$result
    },

    #' @description
    #' Quick content safety check
    #' @param content Content to check
    #' @return TRUE if safe, FALSE otherwise
    is_safe = function(content) {
      result <- self$verify(content)
      isTRUE(result$verified)
    },

    #' @description
    #' Print client info
    print = function() {
      cat("Newton Client\n")
      cat("  Base URL:", self$base_url, "\n")
      cat("  API Key:", if (is.null(self$api_key)) "(none)" else "(set)", "\n")
      cat("  Timeout:", self$timeout, "seconds\n")
      invisible(self)
    }
  )
)

#' Create Newton client (convenience function)
#'
#' @param base_url Base URL of Newton API
#' @param api_key API key for authentication
#' @param timeout Request timeout in seconds
#' @return Newton client instance
#' @export
newton_client <- function(base_url = "http://localhost:8000",
                          api_key = NULL,
                          timeout = 30) {
  Newton$new(base_url, api_key, timeout)
}
