# CODE steps

## The contract

A CODE step is a TypeScript module exporting one function. AP calls it with the resolved `settings.input` map; whatever it returns is the step's output for downstream `{{ <step>.output.field }}` references.

```typescript
export const code = async (inputs) => {
  return { someField: inputs.x };
};
```

```json
"settings": {
  "input": { "x": "{{ trigger.output.body.x }}" },
  "sourceCode": { "code": "export const code = async (inputs) => { … }", "packageJson": "{}" },
  "errorHandlingOptions": { "continueOnFailure": { "value": false }, "retryOnFailure": { "value": false } }
}
```

- The field is `sourceCode.code` (not `body`) and holds the whole module source. `packageJson` is a JSON **string**.
- Templates in `input` are resolved before the call. A value that is exactly one template keeps its native type (object stays object). A template embedded in text is spliced raw with no escaping, so pass objects with templated leaves rather than templating into JSON-shaped strings.
- No top-level `await`; put async work inside `code`.
- Nothing Hegl-related is in `process.env`, and AP does not expand `${VAR}` in `input`.

## What the isolate allows (production runs `SANDBOX_CODE_ONLY`)

Available: ECMAScript built-ins (`Object`, `Array`, `JSON`, `Math`, `Date`, `RegExp`, `Promise`, typed arrays), `async`/`await`, and `inputs`.

Not available (throws or undefined): `console`, `fetch`, `require` and Node built-ins, `Buffer`, `atob`/`btoa`, `TextEncoder`, `URL`, timers, `process`, and every npm package (declared dependencies are stripped; the import fails to compile).

So a CODE step does pure computation only. Anything that needs I/O or a package is a PIECE step (piece actions run in full Node) or a sandbox snapshot via `execute_snapshot_command` (`sandbox-environments.md`). To see what the resolver delivered, temporarily `return { _debug: inputs }` or `throw new Error(JSON.stringify(inputs))`.

## The decision-box pair

A decision box is two steps: the CODE step, then the Hegl piece's `record_decision_box_execution` action.

```json
"settings": {
  "input": { "boxInputs": { "lead": "{{ trigger.output.body.inputs.lead }}" } },
  "sourceCode": {
    "packageJson": "{}",
    "code": "export const code = async (inputs) => { const startTime = Date.now(); const outputs = { /* stub */ }; return { inputs: inputs.boxInputs, outputs, durationMs: Date.now() - startTime }; }"
  },
  "errorHandlingOptions": { "continueOnFailure": { "value": true }, "retryOnFailure": { "value": false } }
}
```

The record step reads `inputs`, `outputs`, `durationMs` off the CODE step, with `activepiecesFlowRunId: "{{ step_start.output.runId }}"` (the id `start_flow_run` returned; AP does not expose its own run id) and the Hegl connection as `auth`. `continueOnFailure: true` keeps the record step running when the box throws; a router afterwards sends the failure to `fail_flow_run` by testing `{{ <step>.output.outputs }}` with `DOES_NOT_EXIST`. Do not test `status == "FAILED"`; it is not reliably exposed.

## Error signatures

| Symptom | Likely cause |
|---|---|
| step never runs, flow hangs on the previous step | top-level `await` or an import that fails to resolve |
| `inputs.x` is `undefined` | a template failed silently: typo in a step or field name |
| `ReferenceError: console is not defined` | isolate limits above; remove the call |
| `Could not resolve "<pkg>"` | npm packages are stripped; move to a piece or snapshot |
