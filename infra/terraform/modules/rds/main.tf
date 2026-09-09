# Uses RDS's native manage_master_user_password rather than hand-rolling a
# Secrets Manager secret + random_password: AWS creates and rotates the secret
# for us, and ECS can pull it directly by ARN (see modules/iam and modules/ecs).

resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db-subnets"
  subnet_ids = var.subnet_ids

  tags = { Name = "${var.name}-db-subnets" }
}

resource "aws_db_parameter_group" "this" {
  name   = "${var.name}-pg16"
  family = "postgres16"

  tags = { Name = "${var.name}-pg16" }
}

resource "aws_db_instance" "this" {
  identifier     = "${var.name}-db"
  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage = var.allocated_storage
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.username

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = var.vpc_security_group_ids
  parameter_group_name   = aws_db_parameter_group.this.name

  multi_az            = var.multi_az
  publicly_accessible = false

  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot

  backup_retention_period = 7

  tags = { Name = "${var.name}-db" }
}
