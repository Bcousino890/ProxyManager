# DataDome Bypass Implementation

This directory contains the implementation of a DataDome bypass solution for the ProxyManager project, specifically designed to work with sites like https://www.idealista.com/inmueble/112835123/

## Features

- Integration with tls-client for advanced HTTP requests
- Browser fingerprinting to mimic real users
- Session management for persistent cookies
- DataDome challenge detection and handling
- Support for residential proxies

## Installation

```bash
pip install tls-client httpx
```

## Usage

The implementation integrates directly with the existing ProxyManager fetch functionality.