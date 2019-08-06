def retry(int times = 5, Closure errorHandler = {e-> log.warn(e.message,e)}, Closure body) {
    def retries = 0
    def exceptions = []
    while(retries++ &lt; times) {
        retries += 1
        try {
          return body.call()
        } catch(e) {}
    }
    throw new Exception("Failed after $times retries")
}