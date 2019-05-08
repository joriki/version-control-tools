# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

variable "cidr_block" {
  description = "CIDR block for the VPC"
}

variable "metadata_bucket_name" {
  description = "Name of the metadata bucket"
}

variable "mirror_ami" {
  description = "AMI ID for mirror instances"
}

variable "route53_zone_id" {
  description = "Route53 private hosted zone ID"
}

variable "taskcluster_vpc_cidr" {
  description = "CIDR block of the Taskcluster VPC in the same AWS region"
}
