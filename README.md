[![Build](https://github.com/Retsumdk/retry-queue-worker/workflows/CI/badge.svg)](https://github.com/Retsumdk/retry-queue-worker/actions)
[![TypeScript](https://img.shields.io/badge/typescript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/node.js-20-green?style=flat-square&logo=node.js&logoColor=white)](https://nodejs.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

# Retry Queue Worker

[![CI](https://github.com/Retsumdk/retry-queue-worker/workflows/CI/badge.svg)](https://github.com/Retsumdk/retry-queue-worker/actions)
[![Node.js](https://img.shields.io/badge/Node.js-20.x-brightgreen.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Exponential backoff retry queue for failed jobs. Handles transient failures with configurable retry policies.

## Features

- **Exponential Backoff** — Automatically retry failed jobs with increasing delays
- **Configurable Policies** — Set max retries, initial delay, and backoff multiplier
- **Dead Letter Queue** — Failed jobs after max retries go to DLQ for manual inspection
- **Priority Support** — Urgent jobs can skip ahead in the queue
- **Metrics** — Track retry counts, success rates, and queue depths

## Installation

```bash
npm install retry-queue-worker
```

## Quick Start

```typescript
import { RetryQueue } from 'retry-queue-worker';

const queue = new RetryQueue({
  maxRetries: 5,
  initialDelayMs: 1000,
  backoffMultiplier: 2,
});

await queue.add('process-payment', { orderId: '12345' });
```

## Related Repos

- [agent-task-queue](https://github.com/Retsumdk/agent-task-queue) — Priority task queue for AI agents
- [distributed-lock-manager](https://github.com/Retsumdk/distributed-lock-manager) — Distributed locking for reliability
- [rate-limiter-middleware](https://github.com/Retsumdk/rate-limiter-middleware) — API rate limiting

## License

MIT License — see [LICENSE](LICENSE)
