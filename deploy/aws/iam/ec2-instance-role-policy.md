Attach these AWS managed policies to the EC2 instance role used by the deploy host:

- `AmazonSSMManagedInstanceCore`
- `AmazonEC2ContainerRegistryReadOnly`

Those are enough for the GitHub Actions workflow to deploy over SSM and for the host
to log in to Amazon ECR and pull the private backend/frontend images.
