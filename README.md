# ec2snapshot

AWS Lambda function to cleanup orphaned AMIs and corresponding EBS snapshots.

## Requirements

The script depends on [boto3](http://boto3.readthedocs.org/en/latest/).  It is provided by AWS lambda at runtime but the library is needed to execute the `upload.py` script locally.

## Installation

Set your AWS token via environment variables:

```bash
$ export AWS_ACCESS_KEY_ID=<XXXXXXXXXXXXXXXX>
$ export AWS_SECRET_ACCESS_KEY=<XXXXXXXXXXXXXXXX>
```

Run the `upload.py` script to setup IAM roles, policies, and lambda function for execution.

```bash
$ python upload.py
```

## Usage

### Dry Run

A dry run can be executed by setting the `DryRun` attribute to `true`.

```json
{
  "DryRun": true
}
```

### Filters

The lambda function can be passed filters as runtime to restrict which EC2 AMIs are affected:

```json
{
  "filters": [
        {
            "Name": "tag:Name",
            "Values": [
                "*NFS*"
            ]
        },
        {
            "Name": "tag:is-public",
            "Values": [
                false
            ]
        }
    ]
}
```

See [boto3 EC2 service resources](http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#service-resource) for full documentation of the supported filters.

### Retention

By default only AMIs older than 30 days will be returned.  The retention period can be customized with the `Retention` attribute:

```json
{
  "Retention": 60
}
```

## Scheduling

Scheduled execution must be set up manually in the lambda console until boto3 adds support.
