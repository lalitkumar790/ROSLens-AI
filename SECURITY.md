# Security Policy

## Reporting a vulnerability
Please use GitHub's private vulnerability reporting feature when available, or contact the maintainer privately. Do not post secrets or exploit details publicly.

## Log privacy
ROS logs can contain usernames, absolute paths, internal hostnames, device identifiers, IP addresses, tokens or other operational details. Redact sensitive data before pasting logs into ROSLens AI, and review your model provider's retention and privacy policy before enabling remote inference.

## Model output
Logs are untrusted input. Model output is not verified truth and must be reviewed by a human. ROSLens AI does not execute suggested commands. Do not run destructive commands suggested by a model without understanding and verifying them.
