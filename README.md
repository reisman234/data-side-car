# data-side-car

This repository contains the sources for data-side-car sub component to the K8sWorkflowBackend.
After the worker-container in a WorkflowJob successfully finishes, and the K8sWorkflowBackend sees this change,
it will send the upload information to the data-side-car do upload data form the result directory into the StorageBackend.