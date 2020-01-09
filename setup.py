from setuptools import setup

setup(
	name='ec2manager',
	version='0.1',
	author="Yaron Lirase Leisersohn",
	description="EC2Manager is a tool to manage EC2 instance state and snapshots",
	license="GPLv3+",
	packages=['shotty'],
	url="https://github.com/leisersohn/ec2manager",
	install_requires=[
		'click',
		'boto3'
	],
	entry_points='''
		[console_scripts]
		shotty=shotty.shotty:cli
	''',

)	
