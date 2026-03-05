import cloudpickle
import inspect

with open(
    "models/production/model_engine/artifacts_bundle/artifacts_bundle.pkl", "rb"
) as f:
    b = cloudpickle.load(f)
print(inspect.getfile(b["transform_fn"]))
