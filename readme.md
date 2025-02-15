``` mermaid 
classDiagram
    class Model {
        +format(system_message, prompt_message, prefix_message)
        +run(system_message, prompt_message, prefix_message)
        +_run(parameter_list)
        +interrupt()
    }
    
    class ChatModel {
        +format(messages)
        +run(messages)
    }
    
    class Agent {
        -model: Model
        -preprocessor: Preprocessor
        -postprocessor: Callable
        +run(system_message, prompt_message, prefix_message)
    }
    
    class Preprocessor {
        +after()
        +then()
        +_process()
    }
    
    class Response {
        -resolver: Callable
        -_result
        +__call__()
    }
    
    class AgentChain {
        -agents: List[Agent]
        +_run()
    }

    Model <|-- ChatModel
    Agent *-- Model
    Agent *-- Preprocessor
    Agent --> Response
    AgentChain --|> Agent
```