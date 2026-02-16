export function getApiErrorMessage(error, fallback = "Something went wrong") {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    if (typeof first === "string" && first.trim()) {
      return first;
    }
    if (first && typeof first === "object") {
      const msg = typeof first.msg === "string" ? first.msg : "";
      const loc = Array.isArray(first.loc) ? first.loc.join(".") : "";
      if (msg && loc) return `${msg} (${loc})`;
      if (msg) return msg;
    }
  }

  if (detail && typeof detail === "object" && typeof detail.message === "string") {
    return detail.message;
  }

  if (typeof error?.message === "string" && error.message.trim()) {
    return error.message;
  }

  return fallback;
}
