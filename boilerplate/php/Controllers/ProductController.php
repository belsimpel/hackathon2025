<?php

namespace App\Controllers;

use App\Services\ProductService;

class ProductController
{
    private ProductService $service;

    public function __construct()
    {
        $this->service = new ProductService();
    }

    public function list(): void
    {
        echo json_encode([
            'message' => 'Product list endpoint (not implemented)',
        ]);
    }
}
