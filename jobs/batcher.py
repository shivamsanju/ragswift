from typing import Any, List


def run_actor_paralelly(actor, method: str, input: List[Any], num_parallel: int = 1):
    actors = [actor.remote() for _ in range(num_parallel)]

    # Dynamically get the method based on the provided method name
    actor_methods = [getattr(actor, method, None) for actor in actors]

    if any(method is None or not callable(method) for method in actor_methods):
        raise ValueError(f"Invalid method: {method}")

    # Split the data into as many batches as actors
    input_batches = [input[i::num_parallel] for i in range(num_parallel)]

    # Process each actor with its corresponding batch
    actorrefs_accumulated = []
    for actor_method, batch in zip(actor_methods, input_batches):
        actorrefs_accumulated.extend([actor_method.remote(item) for item in batch])

    return (actorrefs_accumulated, actors)
