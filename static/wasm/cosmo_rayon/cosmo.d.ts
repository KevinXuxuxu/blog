/* tslint:disable */
/* eslint-disable */
export function main(): void;
/**
 * @param {number} num_threads
 * @returns {Promise<any>}
 */
export function initThreadPool(num_threads: number): Promise<any>;
/**
 * @param {number} receiver
 */
export function wbg_rayon_start_worker(receiver: number): void;
export class PlayerWASM {
  free(): void;
  /**
   * @param {(string)[]} scene
   * @param {number} fr
   * @param {number} w
   * @param {number} h
   * @param {boolean} enable_aabb
   * @param {boolean} disable_shade
   * @param {(string)[]} stl_data_name
   * @param {(Uint8Array)[]} stl_data
   * @returns {PlayerWASM}
   */
  static new(scene: (string)[], fr: number, w: number, h: number, enable_aabb: boolean, disable_shade: boolean, stl_data_name: (string)[], stl_data: (Uint8Array)[]): PlayerWASM;
  /**
   * @returns {(string)[]}
   */
  get_a(): (string)[];
  update(): void;
}
export class wbg_rayon_PoolBuilder {
  free(): void;
  /**
   * @returns {string}
   */
  mainJS(): string;
  /**
   * @returns {number}
   */
  numThreads(): number;
  /**
   * @returns {number}
   */
  receiver(): number;
  build(): void;
}

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
  readonly __wbg_playerwasm_free: (a: number, b: number) => void;
  readonly playerwasm_new: (a: number, b: number, c: number, d: number, e: number, f: number, g: number, h: number, i: number, j: number, k: number) => number;
  readonly playerwasm_get_a: (a: number) => Array;
  readonly playerwasm_update: (a: number) => void;
  readonly main: () => void;
  readonly __wbg_wbg_rayon_poolbuilder_free: (a: number, b: number) => void;
  readonly wbg_rayon_poolbuilder_mainJS: (a: number) => number;
  readonly wbg_rayon_poolbuilder_numThreads: (a: number) => number;
  readonly wbg_rayon_poolbuilder_receiver: (a: number) => number;
  readonly wbg_rayon_poolbuilder_build: (a: number) => void;
  readonly initThreadPool: (a: number) => number;
  readonly wbg_rayon_start_worker: (a: number) => void;
  readonly memory: WebAssembly.Memory;
  readonly __wbindgen_malloc: (a: number, b: number) => number;
  readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
  readonly __wbindgen_export_3: WebAssembly.Table;
  readonly __externref_table_alloc: () => number;
  readonly __externref_drop_slice: (a: number, b: number) => void;
  readonly __wbindgen_free: (a: number, b: number, c: number) => void;
  readonly __wbindgen_exn_store: (a: number) => void;
  readonly __wbindgen_thread_destroy: (a?: number, b?: number, c?: number) => void;
  readonly __wbindgen_start: (a: number) => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;
/**
* Instantiates the given `module`, which can either be bytes or
* a precompiled `WebAssembly.Module`.
*
* @param {{ module: SyncInitInput, memory?: WebAssembly.Memory, thread_stack_size?: number }} module - Passing `SyncInitInput` directly is deprecated.
* @param {WebAssembly.Memory} memory - Deprecated.
*
* @returns {InitOutput}
*/
export function initSync(module: { module: SyncInitInput, memory?: WebAssembly.Memory, thread_stack_size?: number } | SyncInitInput, memory?: WebAssembly.Memory): InitOutput;

/**
* If `module_or_path` is {RequestInfo} or {URL}, makes a request and
* for everything else, calls `WebAssembly.instantiate` directly.
*
* @param {{ module_or_path: InitInput | Promise<InitInput>, memory?: WebAssembly.Memory, thread_stack_size?: number }} module_or_path - Passing `InitInput` directly is deprecated.
* @param {WebAssembly.Memory} memory - Deprecated.
*
* @returns {Promise<InitOutput>}
*/
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput>, memory?: WebAssembly.Memory, thread_stack_size?: number } | InitInput | Promise<InitInput>, memory?: WebAssembly.Memory): Promise<InitOutput>;
