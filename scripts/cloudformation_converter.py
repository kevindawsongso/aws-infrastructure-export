#!/usr/bin/env python3
"""
CloudFormation Converter
Converts AWS infrastructure exports to CloudFormation templates
"""

import json
import sys
import os
from pathlib import Path

def load_json_file(file_path):
    """Load and parse JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return {}

def convert_vpc_to_cf(vpcs_data):
    """Convert VPC data to CloudFormation format"""
    resources = {}
    
    if 'Vpcs' in vpcs_data:
        for i, vpc in enumerate(vpcs_data['Vpcs']):
            vpc_id = vpc.get('VpcId', f'VPC{i}')
            resource_name = f"VPC{vpc_id.replace('-', '')}"
            
            resources[resource_name] = {
                "Type": "AWS::EC2::VPC",
                "Properties": {
                    "CidrBlock": vpc.get('CidrBlock', '10.0.0.0/16'),
                    "EnableDnsHostnames": True,
                    "EnableDnsSupport": True,
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": f"Imported-{vpc_id}"
                        }
                    ]
                }
            }
    
    return resources

def convert_security_groups_to_cf(sg_data):
    """Convert Security Groups to CloudFormation format"""
    resources = {}
    
    if 'SecurityGroups' in sg_data:
        for sg in sg_data['SecurityGroups']:
            if sg.get('GroupName') == 'default':
                continue  # Skip default security groups
                
            sg_id = sg.get('GroupId', '')
            resource_name = f"SecurityGroup{sg_id.replace('-', '')}"
            
            # Convert ingress rules
            ingress_rules = []
            for rule in sg.get('IpPermissions', []):
                cf_rule = {
                    "IpProtocol": rule.get('IpProtocol', 'tcp'),
                    "FromPort": rule.get('FromPort', 80),
                    "ToPort": rule.get('ToPort', 80)
                }
                
                # Add CIDR blocks
                for ip_range in rule.get('IpRanges', []):
                    cf_rule_copy = cf_rule.copy()
                    cf_rule_copy['CidrIp'] = ip_range.get('CidrIp', '0.0.0.0/0')
                    ingress_rules.append(cf_rule_copy)
            
            resources[resource_name] = {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": sg.get('Description', 'Imported security group'),
                    "SecurityGroupIngress": ingress_rules,
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": f"Imported-{sg.get('GroupName', sg_id)}"
                        }
                    ]
                }
            }
    
    return resources

def convert_ec2_to_cf(ec2_data):
    """Convert EC2 instances to CloudFormation format"""
    resources = {}
    
    if 'Reservations' in ec2_data:
        for reservation in ec2_data['Reservations']:
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId', '')
                resource_name = f"EC2Instance{instance_id.replace('-', '')}"
                
                resources[resource_name] = {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "ImageId": instance.get('ImageId', 'ami-0abcdef1234567890'),
                        "InstanceType": instance.get('InstanceType', 't2.micro'),
                        "KeyName": instance.get('KeyName', ''),
                        "SecurityGroupIds": [sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
                        "SubnetId": instance.get('SubnetId', ''),
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": f"Imported-{instance_id}"
                            }
                        ]
                    }
                }
    
    return resources

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 cloudformation_converter.py <export_directory>")
        sys.exit(1)
    
    export_dir = Path(sys.argv[1])
    if not export_dir.exists():
        print(f"Error: Export directory {export_dir} does not exist")
        sys.exit(1)
    
    print(f"Converting exports from {export_dir} to CloudFormation...")
    
    # Load exported data
    vpcs_data = load_json_file(export_dir / 'vpcs.json')
    sg_data = load_json_file(export_dir / 'security-groups.json')
    ec2_data = load_json_file(export_dir / 'ec2-instances.json')
    
    # Convert to CloudFormation resources
    cf_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Imported AWS Infrastructure",
        "Resources": {}
    }
    
    # Add converted resources
    cf_template["Resources"].update(convert_vpc_to_cf(vpcs_data))
    cf_template["Resources"].update(convert_security_groups_to_cf(sg_data))
    cf_template["Resources"].update(convert_ec2_to_cf(ec2_data))
    
    # Write CloudFormation template
    output_file = export_dir / 'cloudformation-template.json'
    with open(output_file, 'w') as f:
        json.dump(cf_template, f, indent=2)
    
    print(f"CloudFormation template created: {output_file}")
    print(f"Resources converted: {len(cf_template['Resources'])}")

if __name__ == "__main__":
    main()

