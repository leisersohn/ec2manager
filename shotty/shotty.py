import boto3
import botocore
import click

def setup_session(profile):
	session = boto3.Session(profile_name=profile)
	global ec2
	ec2 = session.resource('ec2')

	return

def filter_instances(project):
	instances = []
	if project:
		filters = [{'Name':'tag:Project', 'Values':[project]}]
		instances = ec2.instances.filter(Filters=filters)
	else:
		#instances = ec2.instances.all()
		#Hardcode project for testing
		project = 'Valkyrie'
		filters = [{'Name':'tag:Project', 'Values':[project]}]
		instances = ec2.instances.filter(Filters=filters)

	return instances

def has_pending_snapshot(volume):
	snapshots = list(volume.snapshots.all())

	return snapshots and snapshots[0].state == 'pending'

#Define main command line group
@click.group()
@click.option('--profile', default='shotty',
	help="Provide aws config profile (default:shotty)")
def cli(profile):
	"""Shotty manages snapshots"""
	setup_session(profile)	

#Define volumes group and the group commands
@cli.group('volumes')
def volumes():
	"""Commands for Volumes"""

@volumes.command('list')
@click.option('--project', default=None,
	help="Only volumes for tagged project")
def list_volumes(project):
	"List EC2 volumes"

	instances = filter_instances(project)
	
	for i in instances:
		for v in i.volumes.all():
			print(", ".join((
				v.id,
				i.id,
				v.state,
				str(v.size) + "GiB",
				v.encrypted and "Encrypted" or "Not Encrypted"
				)))
	return

#Define snapshots group and the group commands
@cli.group('snapshots')
def snapshots():
	"""Commands for Snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
	help="Only snapshots for tagged project")
@click.option('--all', 'list_all', default=False, is_flag=True,
	help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project, list_all):
	"List EC2 Snapshots"

	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			for s in v.snapshots.all():
				print(", ".join((
					s.id,
					v.id,
					i.id,
					s.state,
					s.progress,
					s.start_time.strftime("%c")
				)))

				#break loop on first successful snapshot	
				if s.state == 'completed' and not list_all: break	
	return

#Define instances group and the group commands
@cli.group('instances')
def instances():
	"""Commands for Instances"""

@instances.command('list')
@click.option('--project', default=None,
	help="Only instances for tagged  project")
@click.option('--force','force_action', default=False, is_flag=True,
	help="Force action (e.g. if project is not provided)") 
def list_instances(project,force_action):
	"List EC2 Instances"

	instances = filter_instances(project)
	
	#perform command if project is set or if force is used
	if project or force_action:	
		for i in instances:
			tags = { t['Key']: t['Value'] for t in i.tags or [] }
			print(', '.join((
				i.id,
				i.instance_type,
				i.placement['AvailabilityZone'],
				i.state['Name'],
				i.public_dns_name,
				tags.get('Project','<no project>')
				)))

	return

@instances.command('stop')
@click.option('--project', default=None,
	help='Only instances for tagged project')
@click.option('--force','force_action', default=False, is_flag=True,
	help="Force action (e.g. if project is not provided)")
def stop_instances(project,force_action):
	"Stop EC2 Instances"

	instances = filter_instances(project)

	#perform command if project is set or if force is used
	if project or force_action:
		for i in instances:
			print("Stopping {0}...".format(i.id))
			try:
				i.stop()
			except botocore.exceptions.ClientError as e:
				print(" Could not stop {0}".format(i.id) + str(e))
				continue

	return

@instances.command('start')
@click.option('--project', default=None,
	help='Only instances for tagged project')
@click.option('--force','force_action', default=False, is_flag=True,
	help="Force action (e.g. if project is not provided)")
def start_instances(project,force_action):
	"Start EC2 Instances"

	instances = filter_instances(project)

	#perform command if project is set or if force is used
	if project or force_action:
		for i in instances:
			print("Starting {0}...".format(i.id))
			try:
				i.start()
			except botocore.exceptions.ClientError as e:
				print(" Could not start {0}".format(i,id) + str(e))
				continue

	return

@instances.command('reboot')
@click.option('--project', default=None,
	help='Only instances for tagged project')
@click.option('--force','force_action', default=False, is_flag=True,
	help="Force action (e.g. if project is not provided)")
def reboot_instances(project,force_action):
	"Reboot EC2 Instances"

	instances = filter_instances(project)

	#perform command if project is set or if force is used
	if project or force_action:
		for i in instances:
			if i.state['Name'] == 'running':
				print("Rebooting {0}...".format(i.id))
				i.reboot()
			else:
				print("Not rebooting {0}. instance is currenlty in state {1}".format(i.id,i.state['Name']))
	
	return

@instances.command('snapshot',
	help="Create snapshots of all volumes")
@click.option('--project', default=None,
	help="Only instances for tagged  project")
@click.option('--force','force_action', default=False, is_flag=True,
        help="Force action (e.g. if project is not provided)")
def create_snapshots(project,force_action):
	"Create snapshots for EC2 Instances"
		
	instances = filter_instances(project)

	#perform command if project is set or if force is used
	if project or force_action:	
		for i in instances:
			print("Stopping {0}...".format(i.id))

			i.stop()
			i.wait_until_stopped()

			for v in i.volumes.all():
				if has_pending_snapshot(v):
					print(" Skipping {0}, snapshot already in progress".format(v.id))
					continue

				print("  Creating snapshot of {0}".format(v.id))
				try:	
					v.create_snapshot(Description="Created by ec2manager")
				except botocore.exceptions.ClientError as e:
					print(" Could not create snapshot for volume {0}".format(v.id) + str(e))
					continue

			print("Starting {0}...".format(i.id))

			i.start()
			i.wait_until_running()

		print("Job's done!")

	return

#main script code
if __name__ == '__main__':
	cli()
