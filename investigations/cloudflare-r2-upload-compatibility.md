# Cloudflare R2 Upload Compatibility Investigation

While developing YachtPass, I investigated a failed upload to Cloudflare R2 that returned:

```text
STREAMING-AWS4-HMAC-SHA256-PAYLOAD-TRAILER not implemented
```

The application used `AWSSDK.S3` version `4.0.100.3` and uploaded streams through `PutObjectRequest`.

## Diagnosis

The upload request did not explicitly configure chunk encoding or payload signing. The error indicated that the request used a streaming Signature Version 4 payload with a checksum trailer that R2 did not support.

Cloudflare documents this compatibility limitation in its [AWS SDK for .NET example](https://developers.cloudflare.com/r2/examples/aws/aws-sdk-net/).

## Implementation change

For the R2 upload path, the application explicitly supplies the known content length and sets:

```csharp
UseChunkEncoding = false;
DisablePayloadSigning = true;
DisableDefaultChecksumValidation = true;
```

`DisablePayloadSigning=true` selects `UNSIGNED-PAYLOAD` and requires HTTPS. The R2 client uses path-style addressing and the `auto` signing region.

These overrides apply only to the R2 path. Other storage providers retain their existing request configuration.

## Integrity tradeoff

Disabling payload signing and default checksum validation removes those SDK integrity checks. HTTPS still protects data in transit.

The application separately calculates and stores a SHA-256 checksum. That stored hash alone does not establish that the remote object matches the original file; verifying that requires reading the object back and comparing its checksum.

## Verification approach

The storage health check uses the same R2 request settings to write a temporary private object, read it back, and delete it. This checks basic storage connectivity and operations; it does not establish correctness for every file size, stream type, or SDK version.

This note documents a compatibility investigation and implementation change. It does not include a standalone reproduction or benchmark dataset.

