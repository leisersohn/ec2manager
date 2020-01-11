# ec2manager

Demo project to manage AWS EC2 instance snapshots

## About

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots.

## Configuring

shotty uses the configuration file created by the AWS cli. e.g. 
`aws configure --profile shotty`

shotty utilizes AWS tagging (Key: 'Project', Value: <Name>) to cotrol all EC2 instance per project

## Running

`pipenv run python shotty/shotty.py <command> <subcommand> <--project=PROJECT>`

*command* is instances, volumes or snapshots
*subcommand* - depends on command
*project* is optional

