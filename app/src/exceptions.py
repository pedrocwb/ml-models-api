class MLModelRequestNotFoundException(Exception):
    pass


class QueueNotFoundException(MLModelRequestNotFoundException):
    pass


class ModelNotFoundException(MLModelRequestNotFoundException):
    pass
