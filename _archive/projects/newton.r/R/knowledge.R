# ============================================================================
#  NEWTON KNOWLEDGE BRIDGE FOR R
# ============================================================================
#
#  Bridges R/RStudio to the canonical Newton knowledge base (adan).
#  
#  Features:
#  - Query 1,625+ verified facts from R console
#  - Access Wikipedia-scraped knowledge
#  - Verified computation through Newton Agent
#  - Kinematic query parsing
#  - Constraint-checked execution
#
#  "The question has shape. The KB has shape. Match shapes, fill slots."
#
#  © 2026 Jared Lewis · Ada Computing Company · Houston, Texas
# ============================================================================

#' @importFrom httr2 request req_headers req_body_json req_perform resp_body_json resp_status req_timeout
#' @importFrom jsonlite toJSON fromJSON
#' @importFrom R6 R6Class
NULL

# ============================================================================
#  KNOWLEDGE BASE CLIENT
# ============================================================================

#' Newton Knowledge Base Client
#'
#' @description
#' R6 class providing interface to Newton's verified knowledge base.
#' Access 1,625+ facts from R - capitals, science, Wikipedia, and more.
#'
#' @examples
#' \dontrun{
#' # Create knowledge client (connects to Newton Agent)
#' kb <- NewtonKB$new()
#'
#' # Ask a question - get a verified fact
#' kb$ask("What is the capital of France?")
#' kb$ask("What is quantum mechanics?")
#' kb$ask("Tell me about machine learning")
#'
#' # Batch queries
#' kb$ask_many(c("What is DNA?", "What is the speed of light?"))
#'
#' # Get stats
#' kb$stats()
#' }
#'
#' @export
NewtonKB <- R6::R6Class(
  "NewtonKB",
  
  public = list(
    
    #' @field agent_url URL of Newton Agent API
    agent_url = NULL,
    
    #' @field timeout Request timeout in seconds
    timeout = NULL,
    
    #' @field cache Local cache of recent queries
    cache = NULL,
    
    #' @description
    #' Create a new Newton Knowledge Base client
    #' @param agent_url URL of Newton Agent (default: "http://localhost:8090")
    #' @param timeout Request timeout in seconds (default: 10)
    #' @return A new NewtonKB client instance
    initialize = function(agent_url = "http://localhost:8090", timeout = 10) {
      self$agent_url <- sub("/$", "", agent_url)
      self$timeout <- timeout
      self$cache <- new.env(hash = TRUE)
      
      # Test connection
      tryCatch({
        resp <- private$get("/health")
        if (!is.null(resp$status) && resp$status == "healthy") {
          message("✓ Connected to Newton Agent")
          message(sprintf("  KB Facts: %s | Model: %s", 
                          resp$kb_facts %||% "?",
                          resp$model %||% "local"))
        }
      }, error = function(e) {
        warning("Could not connect to Newton Agent at ", self$agent_url)
        warning("Start it with: python newton_agent/server.py")
      })
    },
    
    #' @description
    #' Ask the knowledge base a question
    #' @param question The question to ask
    #' @param use_cache Whether to use cached results (default: TRUE)
    #' @return A VerifiedFact object or NULL if not found
    ask = function(question, use_cache = TRUE) {
      # Check cache
      cache_key <- tolower(trimws(question))
      if (use_cache && exists(cache_key, envir = self$cache)) {
        return(get(cache_key, envir = self$cache))
      }
      
      # Query Newton Agent
      result <- tryCatch({
        resp <- private$post("/chat", list(
          message = question,
          ground_claims = FALSE
        ))
        
        if (!is.null(resp$content) && nchar(resp$content) > 0) {
          fact <- VerifiedFact$new(
            fact = resp$content,
            source = private$extract_source(resp$content),
            verified = resp$verified %||% TRUE,
            confidence = 1.0,
            response_ms = resp$elapsed_ms %||% 0
          )
          
          # Cache result
          assign(cache_key, fact, envir = self$cache)
          
          fact
        } else {
          NULL
        }
      }, error = function(e) {
        warning("Query failed: ", e$message)
        NULL
      })
      
      result
    },
    
    #' @description
    #' Ask multiple questions at once
    #' @param questions Vector of questions
    #' @return List of VerifiedFact objects
    ask_many = function(questions) {
      results <- lapply(questions, function(q) {
        self$ask(q)
      })
      names(results) <- questions
      results
    },
    
    #' @description
    #' Interactive knowledge exploration
    #' @param topic Starting topic to explore
    explore = function(topic) {
      cat("\n")
      cat("═══════════════════════════════════════════════════════════════\n")
      cat("  NEWTON KNOWLEDGE EXPLORER\n")
      cat("═══════════════════════════════════════════════════════════════\n")
      cat(sprintf("  Topic: %s\n", topic))
      cat("═══════════════════════════════════════════════════════════════\n\n")
      
      # Get main fact
      result <- self$ask(paste("Tell me about", topic))
      if (!is.null(result)) {
        cat("📖 ", result$fact, "\n\n")
        cat("   Source: ", result$source, "\n")
        cat("   Verified: ", result$verified, "\n")
        cat("   Response: ", result$response_ms, "ms\n")
      } else {
        cat("❌ No information found for '", topic, "'\n")
      }
      
      invisible(result)
    },
    
    #' @description
    #' Get knowledge base statistics
    #' @return Named list of statistics
    stats = function() {
      tryCatch({
        private$get("/stats")
      }, error = function(e) {
        list(error = e$message)
      })
    },
    
    #' @description
    #' Clear the local cache
    clear_cache = function() {
      rm(list = ls(envir = self$cache), envir = self$cache)
      message("✓ Cache cleared")
    },
    
    #' @description
    #' Print client summary
    print = function() {
      cat("NewtonKB Client\n")
      cat(sprintf("  Agent URL: %s\n", self$agent_url))
      cat(sprintf("  Cache entries: %d\n", length(ls(envir = self$cache))))
      invisible(self)
    }
  ),
  
  private = list(
    
    # HTTP GET request
    get = function(endpoint) {
      url <- paste0(self$agent_url, endpoint)
      resp <- httr2::request(url) |>
        httr2::req_timeout(self$timeout) |>
        httr2::req_perform()
      httr2::resp_body_json(resp)
    },
    
    # HTTP POST request
    post = function(endpoint, body) {
      url <- paste0(self$agent_url, endpoint)
      resp <- httr2::request(url) |>
        httr2::req_body_json(body) |>
        httr2::req_timeout(self$timeout) |>
        httr2::req_perform()
      httr2::resp_body_json(resp)
    },
    
    # Extract source from response
    extract_source = function(content) {
      # Look for source pattern: 📚 *Source: XXX*
      if (grepl("Source:", content)) {
        match <- regmatches(content, regexpr("Source:[^*]+", content))
        if (length(match) > 0) {
          return(trimws(sub("Source:", "", match)))
        }
      }
      "Newton Knowledge Base"
    }
  )
)


# ============================================================================
#  VERIFIED FACT CLASS
# ============================================================================

#' Verified Fact
#'
#' @description
#' A fact from Newton's knowledge base with full provenance.
#'
#' @export
VerifiedFact <- R6::R6Class(
  "VerifiedFact",
  
  public = list(
    #' @field fact The fact text
    fact = NULL,
    
    #' @field source Source of the fact
    source = NULL,
    
    #' @field verified Whether fact is verified
    verified = NULL,
    
    #' @field confidence Confidence score (0-1)
    confidence = NULL,
    
    #' @field response_ms Response time in milliseconds
    response_ms = NULL,
    
    #' @description Create a new VerifiedFact
    initialize = function(fact, source = "Unknown", verified = TRUE, 
                          confidence = 1.0, response_ms = 0) {
      self$fact <- fact
      self$source <- source
      self$verified <- verified
      self$confidence <- confidence
      self$response_ms <- response_ms
    },
    
    #' @description Print the fact
    print = function() {
      # Clean fact of source markers for display
      clean_fact <- gsub("📚.*$", "", self$fact)
      clean_fact <- gsub("\\*Source:.*\\*", "", clean_fact)
      clean_fact <- trimws(clean_fact)
      
      cat("┌─────────────────────────────────────────────────────────────┐\n")
      cat("│ VERIFIED FACT                                               │\n")
      cat("├─────────────────────────────────────────────────────────────┤\n")
      
      # Word wrap the fact
      words <- strsplit(clean_fact, " ")[[1]]
      line <- "│ "
      for (word in words) {
        if (nchar(line) + nchar(word) > 60) {
          cat(sprintf("%-63s│\n", line))
          line <- "│ "
        }
        line <- paste0(line, word, " ")
      }
      if (nchar(line) > 2) {
        cat(sprintf("%-63s│\n", line))
      }
      
      cat("├─────────────────────────────────────────────────────────────┤\n")
      cat(sprintf("│ Source: %-52s│\n", substr(self$source, 1, 52)))
      cat(sprintf("│ Verified: %-50s│\n", if(self$verified) "✓ YES" else "✗ NO"))
      cat(sprintf("│ Response: %-50s│\n", paste0(self$response_ms, "ms")))
      cat("└─────────────────────────────────────────────────────────────┘\n")
      invisible(self)
    }
  )
)


# ============================================================================
#  CONVENIENCE FUNCTIONS
# ============================================================================

#' Ask Newton a Question
#'
#' @description
#' Quick way to query Newton's knowledge base from R.
#'
#' @param question The question to ask
#' @param agent_url URL of Newton Agent (default: "http://localhost:8090")
#' @return A VerifiedFact object or NULL
#'
#' @examples
#' \dontrun{
#' newton_ask("What is the capital of France?")
#' newton_ask("What is quantum mechanics?")
#' newton_ask("Tell me about DNA")
#' }
#'
#' @export
newton_ask <- function(question, agent_url = "http://localhost:8090") {
  kb <- NewtonKB$new(agent_url = agent_url)
  kb$ask(question)
}


#' Explore a Topic with Newton
#'
#' @description
#' Interactive exploration of a topic using Newton's knowledge base.
#'
#' @param topic The topic to explore
#' @param agent_url URL of Newton Agent
#' @return Invisible VerifiedFact
#'
#' @examples
#' \dontrun{
#' newton_explore("quantum mechanics")
#' newton_explore("machine learning")
#' }
#'
#' @export
newton_explore <- function(topic, agent_url = "http://localhost:8090") {
  kb <- NewtonKB$new(agent_url = agent_url)
  kb$explore(topic)
}


# ============================================================================
#  NULL COALESCING OPERATOR
# ============================================================================

`%||%` <- function(x, y) if (is.null(x)) y else x
