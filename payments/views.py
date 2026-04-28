import time
import json
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import IdempotencyRecord

@api_view(['POST'])
def process_payment(request):

    idempotency_key = request.headers.get('Idempotency-Key')

    if not idempotency_key:
        return Response(
            {"error": "Idempotency-Key header is required"},
            status=400
        )

    request_body = request.data

    try:
        with transaction.atomic():

            record = IdempotencyRecord.objects.select_for_update() \
                .filter(key=idempotency_key).first()

            
            if not record:
                record = IdempotencyRecord.objects.create(
                    key=idempotency_key,
                    request_body=request_body,
                    status="PROCESSING"
                )

                time.sleep(2)

                response_data = {
                    "message": f"Charged {request_body.get('amount')} {request_body.get('currency')}"
                }

                record.response_body = response_data
                record.status_code = 200
                record.status = "COMPLETED"
                record.save()

                return Response(response_data, status=200)

            
            if record.request_body == request_body:

                while record.status == "PROCESSING":
                    time.sleep(0.1)
                    record.refresh_from_db()

                response = Response(record.response_body, status=record.status_code)
                response['X-Cache-Hit'] = 'true'
                return response

            
            return Response(
                {"error": "Idempotency key already used for a different request body."},
                status=409
            )

    except Exception as e:
        return Response({"error": str(e)}, status=500)
