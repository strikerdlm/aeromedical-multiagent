

# PRISMA 2020 flow diagram for updated systematic reviews which included searches of databases, registers and other sources

```mermaid
flowchart TD
    A[Studies included in<br/>previous version of<br/>review n = ] --> B[Reports of studies<br/>included in previous<br/>version of review n = ]
    
    C[Records identified from*:<br/>Databases n = <br/>Registers n = ] --> D[Records screened<br/>n = ]
    
    E[Records removed before<br/>screening:<br/>Duplicate records removed<br/>n = <br/>Records marked as ineligible<br/>by automation tools n = <br/>Records removed for other<br/>reasons n = ] --> D
    
    F[Records identified from:<br/>Websites n = <br/>Organisations n = <br/>Citation searching n = <br/>etc.] --> G[Reports sought for retrieval<br/>n = ]
    
    D --> H[Records excluded**<br/>n = ]
    D --> I[Reports sought for retrieval<br/>n = ]
    
    I --> J[Reports not retrieved<br/>n = ]
    I --> K[Reports assessed for eligibility<br/>n = ]
    
    G --> L[Reports not retrieved<br/>n = ]
    G --> M[Reports assessed for eligibility<br/>n = ]
    
    K --> N[Reports excluded:<br/>Reason 1 n = <br/>Reason 2 n = <br/>Reason 3 n = <br/>etc.]
    
    M --> O[Reports excluded:<br/>Reason 1 n = <br/>Reason 2 n = <br/>Reason 3 n = <br/>etc.]
    
    K --> P[New studies included in review<br/>n = <br/>Reports of new included studies<br/>n = ]
    
    M --> P
    B --> P
    
    P --> Q[Total studies included in review<br/>n = <br/>Reports of total included studies<br/>n = ]
    
    subgraph " "
        direction TB
        R[Identification]
        S[Screening]
        T[Included]
    end
    
    subgraph "Previous studies"
        A
        B
    end
    
    subgraph "Identification of new studies via databases and registers"
        C
        E
        D
        H
        I
        J
        K
        N
    end
    
    subgraph "Identification of new studies via other methods"
        F
        G
        L
        M
        O
    end
    
    subgraph "Final Results"
        P
        Q
    end
```

*Consider, if feasible to do so, reporting the number of records identified from each database or register searched (rather than the total number across all databases/registers).

**If automation tools were used, indicate how many records were excluded by a human and how many were excluded by automation tools.

Source: Page MJ, et al. BMJ 2021;372:n71. doi: 10.1136/bmj.n71.

This work is licensed under CC BY 4.0. To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/