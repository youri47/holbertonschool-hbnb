"""Services package for HBnB application.

This package contains all the service layer components that implement the business logic
of the application. It follows a clean architecture pattern where services orchestrate
the interaction between the API layer and the persistence layer.

Each service is implemented as a singleton and can be imported directly from their
respective modules. The facade module provides a unified interface (HBnBFacade)
that coordinates between different services.

Modules:
    - facade: Provides the HBnBFacade class for coordinated access to services
    - user_service: Manages user-related operations (singleton: user_service)
    - place_service: Handles place management and search (singleton: place_service)
    - review_service: Manages property reviews (singleton: review_service)
    - amenity_service: Handles property amenities/features (singleton: amenity_service)
"""