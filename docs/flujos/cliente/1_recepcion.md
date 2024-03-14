```mermaid
sequenceDiagram
    participant Client
    participant Cashier
    participant Backend
    Client->>Cashier: Enter bar and provide details
    Cashier->>Backend: Register client and create new order
    Backend->>Backend: Associate card with client and order
    Backend-->>Cashier: Confirm registration and order creation
    Cashier-->>Client: Hand over associated card
```