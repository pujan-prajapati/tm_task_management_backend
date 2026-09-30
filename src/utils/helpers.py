def success_response(data, message: str = "Request successful"):
    return {"data": data, "success": True, "message": message}
