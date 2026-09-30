output "alb_dns_name" {
  value = aws_lb.this.dns_name
}

output "cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "cluster_arn" {
  value = aws_ecs_cluster.this.arn
}

output "service_name" {
  value = aws_ecs_service.api.name
}

# The deploy workflow runs `alembic upgrade head` as a one-off RunTask using
# this same task definition (overriding the container command) before
# rolling the service onto a new image — see deploy.yml and the github-oidc
# module's EcsRunMigrationTask policy statement. Built from scratch (rather
# than string-replacing the revision suffix off aws_ecs_task_definition.api.arn)
# because a naive replace(arn, ":${revision}", ":*") can also match a ":<digit>"
# that appears earlier in the ARN, e.g. inside the account id — revision-less
# (":*") since the revision number only changes on a `terraform apply`, not on
# every deploy, and a stale pinned revision would silently block RunTask.
output "task_definition_family_arn" {
  value = "arn:aws:ecs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:task-definition/${aws_ecs_task_definition.api.family}:*"
}
