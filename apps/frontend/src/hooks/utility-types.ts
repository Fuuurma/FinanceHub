import { Ref, RefCallback } from 'react'

export type CallbackRef<T> = RefCallback<T> | Ref<T> | null
