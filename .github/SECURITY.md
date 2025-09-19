# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

1. **Do not create a public GitHub issue** for security vulnerabilities
2. **Email us directly** at security@console-hax.com with:
   - A detailed description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Any suggested fixes

3. **We will respond within 48 hours** to acknowledge receipt
4. **We will provide regular updates** on our progress in addressing the issue
5. **We will credit you** in our security advisories (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

- Always verify checksums before installing firmware or memory card images
- Keep your MemCard PRO2 firmware updated
- Use strong, unique passwords for FTP access
- Regularly review device access logs
- Only download files from trusted sources

### For Developers

- Follow secure coding practices
- Use dependency scanning tools
- Implement proper input validation
- Use secure communication protocols (HTTPS, SFTP when possible)
- Regular security audits and code reviews

## Security Features

- Configuration files created with secure permissions (600)
- FTP credentials stored with appropriate access controls
- Checksum verification for all distributed files
- Secure dependency management with version pinning
- Regular security updates and patches

## Dependencies

We regularly monitor and update dependencies for security vulnerabilities:

- `zeroconf` - For device discovery
- `requests` - For HTTP operations
- `psutil` - For system monitoring
- `PyYAML` - For configuration management

## Contact

For security-related questions or concerns, please contact:
- Email: security@console-hax.com
- GitHub: Create a private security advisory

## Acknowledgments

We thank the security researchers and community members who help keep our projects secure.
