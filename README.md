# ec2manager

Demo project to manage AWS EC2 instance snapshots

## About

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots.

## Configuring

shotty uses the configuration file created by the AWS cli. e.g. 
`aws configure --profile shotty`

shotty utilizes AWS tagging (Key: 'Project', Value: <Name>) to control all EC2 instance per project

## Running

`pipenv run python shotty/shotty.py <--profile=PROFILE> <--region=AWS_REGION> <command> <subcommand> <--project=PROJECT> <--force>`

*profile* is the AWS profile configuration (default:shotty)

*region* is the AWS region (default comes from --profile)

*command* is instances, volumes or snapshots

*subcommand* - depends on command

*project* is optional (default: Valkyrie)

*force* is optional to force command if no project is specified
