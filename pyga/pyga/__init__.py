__version__ = "0.1.2b"
try:
    from ga import GATracker, DjangoGATracker, FlaskGATracker
except ImportError:
    pass