import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
	instances = []
	if project:
		filters = [{'Name':'tag:Project', 'Values':[project]}]
		instances = ec2.instances.filter(Filters=filters)
	else:
		#instances = ec2.instances.all()
		instances = []

	return instances

#Define main command line group
@click.group()
def cli():
	"""Shotty manages snapshots"""

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
def list_snapshots(project):
	"List Snapshots"

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
	return

#Define instances group and the group commands
@cli.group('instances')
def instances():
	"""Commands for Instances"""

@instances.command('list')
@click.option('--project', default=None,
	help="Only instances for tagged  project")
def list_instances(project):
	"List EC2 Instances"
	instances = filter_instances(project)
	
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
def stop_instances(project):
	"Stop EC2 Instances"

	instances = filter_instances(project)

	for i in instances:
		print("Stopping {0}...".format(i.id))
		i.stop()

	return

@instances.command('start')
@click.option('--project', default=None,
	help='Only instances for tagged project')
def start_instances(project):
	"Start EC2 Instances"

	instances = filter_instances(project)

	for i in instances:
		print("Starting {0}...".format(i.id))
		i.start()

	return

@instances.command('snapshot',
	help="Create snapshots of all volumes")
@click.option('--project', default=None,
	help="Only instances for tagged  project")
def create_snapshots(project):
	"Create snapshots for EC2 Instances"
		
	instances = filter_instances(project)

	for i in instances:
		print("Stopping {0}...".format(i.id))

		i.stop()
		i.wait_until_stopped()

		for v in i.volumes.all():
			print("  Creating snapshot of {0}".format(v.id))
			v.create_snapshot(Description="Created by ec2manager")

		print("Starting {0}...".format(i.id))

		i.start()
		i.wait_until_running()

	print("Job's done!")

	return

#main script code
if __name__ == '__main__':
	cli()
