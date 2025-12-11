<?php

require __DIR__ . '/vendor/autoload.php';

use App\Controllers\ProductController;
use App\Controllers\CartController;
use App\Controllers\CheckoutController;

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

switch ($uri) {

    case '/products':
        (new ProductController())->list();
        break;

    case '/cart':
        (new CartController())->view();
        break;

    case '/cart/add':
        (new CartController())->add();
        break;

    case '/checkout':
        (new CheckoutController())->process();
        break;

    default:
        http_response_code(404);
        echo json_encode(['error' => 'Not Found']);
}
