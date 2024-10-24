"""TcEx Framework Module"""

# standard library
import functools
from collections.abc import Callable, Container
from typing import TYPE_CHECKING, Any, TypeVar

# third-party
from redis import Redis

if TYPE_CHECKING:
    from .app.app import App
    from .app.playbook.playbook import Playbook
    from .app.token import Token
    from .exit.exit import Exit
    from .input.input import Input
    from .logger.logger import Logger
    from .requests_tc import RequestsTc, TcSession

T = TypeVar('T')


class Registry(Container):
    """Dynamic service registry that supports raw values, factories, and factory providers.

    Terms:
        Service - An object that is registered with this registry and can be retrieved from it by
            type or name.
        Factory - A callable that can return an instance that fulfills a type or name.
        Provider - An object with one or more members that are factories (as denoted by the
            @factory decorator)
    """

    def __init__(self):
        """Initialize instance properties."""
        self._values = {}

    def add_service(self, type_or_name: str | type, value: Any):
        """Add an instance of a type to this registry.

        A service is a single instance of the given type.

        Args:
            type_or_name: the concrete type of the provided service, or a name (MyClass or
            'MyClass')
            value: The service.
        """
        self._add(type_or_name, value)

    def add_method(self, method: Callable):
        """Add an instance method to the registry.

        Args:
            method: A instance method to add to the registry.
        """
        self._add(method.__name__, method)

    def add_factory(self, type_or_name: str | type, factory: Callable, singleton=False):
        """Add a factory for a service.

        A factory is any callable that can be invoked to provide the given type of service.

        Args:
            type_or_name: the concrete type of the provided service, or a name (MyClass or
            'MyClass')
            factory: the callable that can create the above type.
            singleton: if True, the factory will be invoked exactly once.  If False, the factory
            will be invoked every time the service is requested.
        """
        self._add(type_or_name, (singleton, factory))

    def register(self, provider):
        """Add a provider, which provides one or more service factories.

        A provider is a class with one or more members decorated with Registry@factory.
        When you add a provider with this method, each of its decorated members will be added to
        this registry as a factory.
        """
        for entry in dir(provider):
            try:
                provider_function = type(provider).__dict__[entry]
                factory_provider = getattr(provider_function, 'factory_provider', None)
                if factory_provider:
                    provided_type, singleton = factory_provider
                    if callable(provider_function):  # A function or member function
                        # if it's a bound method, this will get the bound version
                        provider_member = getattr(provider, entry)
                        self.add_factory(provided_type, provider_member, singleton)
                    elif hasattr(provider_function, '__get__'):
                        # this is a property or non-callable descriptor:
                        self.add_factory(
                            provided_type,
                            functools.partial(provider_function.__get__, provider, provider),
                            singleton,
                        )
                    else:
                        self.add_service(provided_type, provider_function)
            except KeyError:
                pass

    def _add(self, type_or_name: str | type, value: Callable | type | tuple[bool, Callable]):
        """Add a service to the registry."""
        key = type_or_name if isinstance(type_or_name, str) else type_or_name.__name__
        self._values[key] = value

    def __getattr__(self, type_or_name):
        """Enable property-access style access to registered services, i.e., registry.MyClass."""
        return self._retrieve_registered_value(type_or_name)

    def __contains__(self, item: Any) -> bool:
        """Enable the syntax MyClass in registry."""
        try:
            self.__getattr__(item)
            return True
        except RuntimeError:
            return False

    def _retrieve_registered_value(self, type_or_name):
        """Retrieve or create a value, if already registered."""
        key = type_or_name if isinstance(type_or_name, str) else type_or_name.__name__
        if key in self._values:
            value = self._values[key]
            if isinstance(value, tuple):
                singleton, factory = value
                if not singleton:
                    return factory()

                value = factory()
                self._values[key] = value

            return value

        raise RuntimeError(f'No provider for type: {key}')

    def _reset(self):
        """Only used during testing to reset registry."""
        self._values = {}

    @staticmethod
    def factory(type_or_name: str | type, singleton: bool = False) -> Callable[[T], T]:
        """Decorate a function that can be treated as a factory that provides a service.

        Args:
            type_or_name: the concrete type of the provided service, or a name (MyClass or
            'MyClass')
            singleton: if True, the factory will be invoked exactly once.  If False, the factory
            will be invoked every time the service is requested.
        """

        def _decorator(original: T) -> T:
            setattr(original, 'factory_provider', (type_or_name, singleton))
            return original

        return _decorator

    #
    # The below are convenience-wrappers that make it easier to retrieve services from the registry.
    #

    @property
    def app(self) -> 'App':
        """Return App object."""
        return self.App

    @property
    def exit(self) -> 'Exit':
        """Return Exit object."""
        return self.Exit

    @property
    def inputs(self) -> 'Input':
        """Return an Inputs object."""
        return self.Input

    @property
    def logger(self) -> 'Logger':
        """Return an Inputs object."""
        return self.Logger

    @property
    def playbook(self) -> 'Playbook':
        """Return a Playbook object."""
        return self.app.playbook

    @property
    def redis_client(self) -> Redis:
        """Return a Redis client object (redis.Redis)."""
        return self.app.key_value_store.redis_client

    @property
    def request_tc(self) -> 'RequestsTc':
        """Return a TcSession."""
        return self.RequestsTc

    @property
    def session_tc(self) -> 'TcSession':
        """Return a TcSession."""
        return self.request_tc.session

    @property
    def token(self) -> 'Token':
        """Return a Token."""
        return self.app.token


registry = Registry()
