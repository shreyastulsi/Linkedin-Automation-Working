flowchart LR
  subgraph Client
    B[User Browser]
    SW[Service Worker]
  end

  subgraph Frontend
    PWA[React PWA (built by Vite)]
  end

  subgraph Server
    ES[Express API Server]
    ┌─────────────────────────┐
    │ Middleware Layer        │
    │ ┌──────────┐ ┌─────────┐│
    │ │ Auth     │ │ Rate-   ││
    │ │ (JWT)    │ │ Limiter ││
    │ └──────────┘ └─────────┘│
    │ ┌──────────┐            │
    │ │ Logger   │            │
    │ └──────────┘            │
    └─────────────────────────┘
    subgraph Routes
      A[/api/auth\] 
      U[/api/users\] 
      Pr[/api/products\] 
      Pa[/api/pantry\] 
      G[/api/goals\] 
      AI[/api/ai\]
    end

    PC[Prisma Client]
    RC[Redis Cache]
    DB[(PostgreSQL DB)]
    OA[(OpenAI API)]
  end

  B --> SW
  SW --> PWA
  PWA -- HTTPS --> ES

  ES -->|passes through| Auth
  ES --> Rate-Limiter
  ES --> Logger

  ES --> A
  ES --> U
  ES --> Pr
  ES --> Pa
  ES --> G
  ES --> AI

  A & U & Pr & Pa & G --> PC
  PC --> DB

  Pa --> RC
  RC --> DB

  AI --> OA
