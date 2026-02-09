from core import app
from core.data import inventory
from webob import Request, Response
from roob.constants import HttpStatus
from core.service.product_service import ProductService


@app.route('/api/products')
class ProductCreatController:
    def __init__(self):
        self.service = ProductService()

    def get(self, request: Request) -> Response:
        return Response(
            json_body=self.service.get_all_products()
        )

    # Create
    def post(self, request: Request) -> Response:
        products = self.service.create_new_product(
            request.json
        )
        return Response(
            json_body=products
        )


@app.route('/api/products/{id:d}')
class ProductModifyController:
    def __init__(self):
        self.service = ProductService()

    def _get_product_not_found_response(self, product_id: int) -> Response:
        return Response(
            json_body={
                "message": f"No product found with product id {product_id}"
            },
            status=HttpStatus.NOT_FOUND
        )

    def get(self, request: Request, id: int) -> Response:
        product = self.service.get_product_by_id(id)
        if not product:
            return self._get_product_not_found_response(id)
        return Response(
            json_body=product
        )

    def delete(self, request: Request, id: int):
        try:
            products = self.service.delete_product_by_id(id)
            return Response(
                json_body=products
            )
        except Exception as e:
            return Response(
                json_body={"message": str(e)},
                status=HttpStatus.NOT_FOUND
            )


@app.route('/api/products/{category}')
def get_products_by_cat(request: Request, category: str) -> Response:
    if category not in inventory:
        return Response(
            json_body={
                "message": f"{category} doesn't exist in the inventory",
            },
            status=HttpStatus.NOT_FOUND,
        )
    return Response(
        json_body=inventory[category],
    )