from typing import Generic, TypeVar, cast

from django.db import models

from resilient_logger.models.lazy_init_model_protocol import LazyInitModelProtocol

TLazyInitModelProtocol = TypeVar("TLazyInitModelProtocol", bound=LazyInitModelProtocol)


class LazyInitTableManager(models.Manager, Generic[TLazyInitModelProtocol]):
    def get_queryset(self):
        model = cast(TLazyInitModelProtocol, self.model)
        model._initialized = model.init_model()
        return super().get_queryset()
