try:
    from audioop_lts import *
except ImportError:
    import audioop as audioop_lts # For older python versions
    from audioop import *
