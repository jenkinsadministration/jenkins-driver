def retry(int times = 3, Closure errorHandler = {e-> log.warn(e.message,e)}, Closure body) {
  int retries = 0
  def exceptions = []
  while(retries++ < times) {
    try {
      return body.call()
    } catch(e) {
      exceptions << e
      errorHandler.call(e)
    }
  }
  throw new MultipleFailureException("Failed after $times retries", exceptions)
}