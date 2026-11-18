resource "aws_ecs_cluster" "main" {
  name = "uptime"
}

resource "aws_service_discovery_http_namespace" "main" {
  name = "uptime"
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/uptime"
  retention_in_days = 7
}

resource "aws_iam_role" "ecs" {
  name = "uptime-ecs"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs" {
  role       = aws_iam_role.ecs.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
