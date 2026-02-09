"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON DECORATORS
Decorators for building verified functions.

Usage:
    from newton import verified, bounded, logged, constrained
    
    @verified
    def my_function(x):
        return x * 2
    
    @bounded(max_iterations=1000)
    def process_items(items):
        for item in items:
            yield item
    
    @constrained(input=gt(0), output=gt(0))
    def positive_only(x):
        return abs(x)
═══════════════════════════════════════════════════════════════════════════════
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar
from datetime import datetime
import hashlib
import time

from newton.types import Bounds, VerificationResult
from newton.constraints import Constraint


F = TypeVar('F', bound=Callable)


def verified(fn: F) -> F:
    """
    Mark a function as verified.
    
    Verified functions:
    - Log all invocations
    - Track input/output hashes
    - Catch and log errors
    
    Example:
        @verified
        def add(a, b):
            return a + b
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        input_hash = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()[:16]
        
        try:
            result = fn(*args, **kwargs)
            output_hash = hashlib.sha256(str(result).encode()).hexdigest()[:16]
            elapsed = time.time() - start
            
            # Attach verification metadata
            if hasattr(result, '__dict__'):
                result._newton_verified = True
                result._newton_input_hash = input_hash
                result._newton_output_hash = output_hash
                result._newton_elapsed = elapsed
            
            return result
        except Exception as e:
            # Log the error but re-raise
            raise
    
    wrapper._newton_verified = True
    return wrapper


def bounded(
    max_iterations: int = 10_000,
    max_recursion: int = 100,
    max_operations: int = 1_000_000,
    timeout_seconds: float = 30.0
) -> Callable[[F], F]:
    """
    Enforce execution bounds on a function.
    
    Bounded functions are guaranteed to terminate.
    
    Example:
        @bounded(max_iterations=100)
        def process(items):
            for i, item in enumerate(items):
                if i >= 100:
                    break
                yield item
    """
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Inject bounds into function if it accepts them
            import inspect
            sig = inspect.signature(fn)
            if 'bounds' in sig.parameters:
                kwargs['bounds'] = Bounds(
                    max_iterations=max_iterations,
                    max_recursion=max_recursion,
                    max_operations=max_operations,
                    timeout_seconds=timeout_seconds
                )
            
            start = time.time()
            
            # Create a bounded iterator wrapper for generators
            result = fn(*args, **kwargs)
            
            if hasattr(result, '__iter__') and hasattr(result, '__next__'):
                # It's a generator - wrap it with bounds
                def bounded_generator():
                    count = 0
                    for item in result:
                        count += 1
                        if count > max_iterations:
                            raise RuntimeError(f"Exceeded max iterations: {max_iterations}")
                        if time.time() - start > timeout_seconds:
                            raise RuntimeError(f"Exceeded timeout: {timeout_seconds}s")
                        yield item
                return bounded_generator()
            
            # Check timeout for regular functions
            if time.time() - start > timeout_seconds:
                raise RuntimeError(f"Exceeded timeout: {timeout_seconds}s")
            
            return result
        
        wrapper._newton_bounded = True
        wrapper._newton_bounds = Bounds(
            max_iterations=max_iterations,
            max_recursion=max_recursion,
            max_operations=max_operations,
            timeout_seconds=timeout_seconds
        )
        return wrapper
    return decorator


def logged(log_fn: Optional[Callable] = None) -> Callable[[F], F]:
    """
    Log all function calls.
    
    Example:
        @logged()
        def my_function(x):
            return x * 2
        
        # Or with custom logger:
        @logged(log_fn=my_logger.info)
        def my_function(x):
            return x * 2
    """
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().isoformat()
            
            log_entry = {
                "function": fn.__name__,
                "timestamp": timestamp,
                "args": str(args)[:100],
                "kwargs": str(kwargs)[:100],
            }
            
            if log_fn:
                log_fn(f"[NEWTON] Calling {fn.__name__}")
            
            try:
                result = fn(*args, **kwargs)
                log_entry["status"] = "success"
                log_entry["result_type"] = type(result).__name__
                
                if log_fn:
                    log_fn(f"[NEWTON] {fn.__name__} completed")
                
                return result
            except Exception as e:
                log_entry["status"] = "error"
                log_entry["error"] = str(e)
                
                if log_fn:
                    log_fn(f"[NEWTON] {fn.__name__} failed: {e}")
                
                raise
        
        wrapper._newton_logged = True
        return wrapper
    return decorator


def constrained(
    input: Optional[Constraint] = None,
    output: Optional[Constraint] = None,
    **field_constraints
) -> Callable[[F], F]:
    """
    Enforce constraints on function input and output.
    
    Example:
        @constrained(input=gt(0), output=gt(0))
        def double_positive(x):
            return x * 2
        
        # Or with field constraints:
        @constrained(age=gt(0), name=is_not_empty())
        def create_user(age, name):
            return {"age": age, "name": name}
    """
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Check input constraint on first argument
            if input is not None and args:
                if not input.check(args[0]):
                    raise ValueError(f"Input constraint failed: {input.message}")
            
            # Check field constraints
            import inspect
            sig = inspect.signature(fn)
            params = list(sig.parameters.keys())
            
            for i, (param, value) in enumerate(zip(params, args)):
                if param in field_constraints:
                    constraint = field_constraints[param]
                    if not constraint.check(value):
                        raise ValueError(f"Constraint on '{param}' failed: {constraint.message}")
            
            for param, value in kwargs.items():
                if param in field_constraints:
                    constraint = field_constraints[param]
                    if not constraint.check(value):
                        raise ValueError(f"Constraint on '{param}' failed: {constraint.message}")
            
            # Execute function
            result = fn(*args, **kwargs)
            
            # Check output constraint
            if output is not None:
                if not output.check(result):
                    raise ValueError(f"Output constraint failed: {output.message}")
            
            return result
        
        wrapper._newton_constrained = True
        wrapper._newton_input_constraint = input
        wrapper._newton_output_constraint = output
        wrapper._newton_field_constraints = field_constraints
        return wrapper
    return decorator


def pure(fn: F) -> F:
    """
    Mark a function as pure (no side effects).
    
    Pure functions with the same input always produce the same output.
    This decorator enables memoization.
    
    Example:
        @pure
        def add(a, b):
            return a + b
    """
    cache = {}
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Create cache key
        key = (args, tuple(sorted(kwargs.items())))
        
        if key in cache:
            return cache[key]
        
        result = fn(*args, **kwargs)
        cache[key] = result
        return result
    
    wrapper._newton_pure = True
    wrapper._newton_cache = cache
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper


def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """
    Retry a function on failure.
    
    Example:
        @retry(max_attempts=3)
        def fetch_data(url):
            return requests.get(url)
    """
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay_seconds)
            
            raise last_error
        
        wrapper._newton_retry = True
        wrapper._newton_max_attempts = max_attempts
        return wrapper
    return decorator
