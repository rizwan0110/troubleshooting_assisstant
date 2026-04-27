from dataclasses import dataclass


@dataclass
class TimeoutConfig:
    connect: float = 5.0  # seconds to establish connection
    read: float = 30.0  # seconds to wait for response


timeout_config = TimeoutConfig()
