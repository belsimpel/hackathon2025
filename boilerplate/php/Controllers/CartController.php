<?php

namespace App\Controllers;

use App\Services\CartService;

class CartController
{
    private CartService $service;

    public function __construct()
    {
        $this->service = new CartService();
    }

    public function view(): void
    {
        echo json_encode([
            'message' => 'View cart endpoint (not implemented)',
        ]);
    }

    public function add(): void
    {
        echo json_encode([
            'message' => 'Add to cart endpoint (not implemented)',
        ]);
    }
}
