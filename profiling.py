"""Profiling utilities for performance analysis."""

import cProfile
import pstats
import io
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

try:
    from line_profiler import LineProfiler
    HAS_LINE_PROFILER = True
except ImportError:
    HAS_LINE_PROFILER = False
    print("Warning: line_profiler not installed. Line profiling disabled.")


class ProfilerConfig:
    """Configuration for profiling runs."""
    def __init__(self, 
                 enabled=False,
                 line_profile=False,
                 output_dir='profiling_results',
                 functions_to_profile=None):
        self.enabled = enabled
        self.line_profile = line_profile and HAS_LINE_PROFILER
        self.output_dir = Path(output_dir)
        self.functions_to_profile = functions_to_profile or []
        
        if self.enabled:
            self.output_dir.mkdir(exist_ok=True)


@contextmanager
def profile_context(config, run_name="simulation"):
    """
    Context manager for profiling code blocks.
    
    Usage:
        with profile_context(config, "my_run"):
            # your code here
    """
    if not config.enabled:
        yield None
        return
    
    # Setup profilers
    c_profiler = cProfile.Profile()
    l_profiler = LineProfiler() if config.line_profile else None
    
    # Add functions for line profiling
    if l_profiler:
        for func in config.functions_to_profile:
            l_profiler.add_function(func)
    
    # Start profiling
    c_profiler.enable()
    if l_profiler:
        l_profiler.enable()
    
    try:
        yield {'cprofile': c_profiler, 'line_profile': l_profiler}
    finally:
        # Stop profiling
        c_profiler.disable()
        if l_profiler:
            l_profiler.disable()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save cProfile results
        c_output = config.output_dir / f"{run_name}_cprofile_{timestamp}.txt"
        with open(c_output, 'w') as f:
            s = io.StringIO()
            ps = pstats.Stats(c_profiler, stream=s)
            ps.sort_stats('cumulative')
            ps.print_stats(50)  # Top 50 functions
            f.write(s.getvalue())
        print(f"cProfile results saved to: {c_output}")
        
        # Save line profiler results
        if l_profiler:
            l_output = config.output_dir / f"{run_name}_lineprof_{timestamp}.txt"
            with open(l_output, 'w') as f:
                s = io.StringIO()
                l_profiler.print_stats(stream=s)
                f.write(s.getvalue())
            print(f"Line profiler results saved to: {l_output}")


def profile_function(config):
    """
    Decorator for profiling individual functions.
    
    Usage:
        @profile_function(profiler_config)
        def my_function():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not config.enabled:
                return func(*args, **kwargs)
            
            with profile_context(config, func.__name__):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator